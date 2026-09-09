import json
from datetime import datetime, timezone
from pathlib import Path

from app.agents.revision_agent import RevisionAgent
from app.agents.verification_agent import VerificationAgent
from app.models.analysis import AnalysisAssessment

from scripts.evaluation.adversarial_cases import (
    AdversarialCase,
    get_adversarial_cases,
)


RESULTS_DIR = (
    Path(__file__).resolve().parent / "results"
)


# ============================================================
# Evaluate one adversarial case
# ============================================================

def evaluate_case(
    case: AdversarialCase,
    verifier: VerificationAgent,
    reviser: RevisionAgent,
) -> dict:

    print()
    print("=" * 70)
    print(
        f"ADVERSARIAL CASE: {case.name}"
    )
    print("=" * 70)

    print(case.description)

    result = {
        "case_name": case.name,

        "expected_verifier_rejection": (
            case.expected_verifier_rejection
        ),

        "verifier_rejected": False,

        "verification_issues": [],

        "revision_attempted": False,

        "revision_valid": False,

        "revision_error": None,

        "revision_succeeded": False,

        "final_verifier_approved": False,

        "final_verification_issues": [],

        "error": None,
    }

    try:

        # ----------------------------------------------------
        # Step 1
        # Verify intentionally bad analysis
        # ----------------------------------------------------

        print(
            "\nRunning VerificationAgent "
            "on bad analysis..."
        )

        verification = verifier.verify(
            operations=case.operations,
            weather=case.weather,
            analysis=case.bad_analysis,
        )

        result["verifier_rejected"] = (
            not verification.approved
        )

        result["verification_issues"] = (
            verification.issues
        )

        print(
            f"Verifier approved: "
            f"{verification.approved}"
        )

        if verification.issues:

            print(
                "\nDetected issues:"
            )

            for issue in verification.issues:

                print(
                    f"- {issue}"
                )

        # ----------------------------------------------------
        # Step 2
        # Require verifier rejection
        # ----------------------------------------------------

        if not result["verifier_rejected"]:

            print(
                "\nFAIL: Verifier failed to reject "
                "the adversarial analysis."
            )

            return result

        # ----------------------------------------------------
        # Step 3
        # Run RevisionAgent
        # ----------------------------------------------------

        result["revision_attempted"] = True

        print(
            "\nRunning RevisionAgent..."
        )

        revised_analysis = reviser.revise(
            operations=case.operations,
            weather=case.weather,
            analysis=case.bad_analysis,
            verification=verification,
        )

        # ----------------------------------------------------
        # Step 4
        # Validate revised analysis
        # ----------------------------------------------------

        try:

            revised_analysis = (
                AnalysisAssessment.model_validate(
                    revised_analysis
                )
            )

            result["revision_valid"] = True

        except Exception as error:

            result["revision_error"] = (
                "Revised analysis failed schema validation: "
                f"{error}"
            )

            print(
                f"\n{result['revision_error']}"
            )

            return result

        print(
            "\nRevised analysis:"
        )

        print(
            revised_analysis.overall_assessment
        )

        print(
            f"\nRevised airport: "
            f"{revised_analysis.airport}"
        )

        print(
            f"Revised disruption_detected: "
            f"{revised_analysis.disruption_detected}"
        )

        print(
            f"Revised weather_risk_detected: "
            f"{revised_analysis.weather_risk_detected}"
        )

        print(
            f"Revised confidence: "
            f"{revised_analysis.confidence}"
        )

        # ----------------------------------------------------
        # Step 5
        # Verify revised analysis
        # ----------------------------------------------------

        print(
            "\nRunning VerificationAgent "
            "on revised analysis..."
        )

        final_verification = verifier.verify(
            operations=case.operations,
            weather=case.weather,
            analysis=revised_analysis,
        )

        result["final_verifier_approved"] = (
            final_verification.approved
        )

        result["final_verification_issues"] = (
            final_verification.issues
        )

        # ----------------------------------------------------
        # Step 6
        # Determine revision success
        # ----------------------------------------------------

        result["revision_succeeded"] = (
            result["verifier_rejected"]
            and result["revision_valid"]
            and result["final_verifier_approved"]
        )

        print(
            f"\nFinal verifier approved: "
            f"{final_verification.approved}"
        )

        if final_verification.issues:

            print(
                "\nRemaining verification issues:"
            )

            for issue in final_verification.issues:

                print(
                    f"- {issue}"
                )

        print(
            f"\nRevision succeeded: "
            f"{result['revision_succeeded']}"
        )

        return result

    except Exception as error:

        result["error"] = str(error)

        print(
            f"\nERROR: {error}"
        )

        return result


# ============================================================
# Summary calculation
# ============================================================

def calculate_summary(
    results: list[dict],
) -> dict:

    total = len(results)

    if total == 0:

        return {
            "total_cases": 0,
            "verifier_detection_rate": None,
            "revision_success_rate": None,
            "final_approval_rate": None,
        }

    # --------------------------------------------------------
    # Verifier detection
    # --------------------------------------------------------

    verifier_detection_rate = (
        sum(
            result["verifier_rejected"]
            for result in results
        )
        / total
    )

    # --------------------------------------------------------
    # Revision success
    # --------------------------------------------------------

    revision_cases = [
        result
        for result in results
        if result["revision_attempted"]
    ]

    if revision_cases:

        revision_success_rate = (
            sum(
                result["revision_succeeded"]
                for result in revision_cases
            )
            / len(revision_cases)
        )

    else:

        revision_success_rate = None

    # --------------------------------------------------------
    # Final approval
    # --------------------------------------------------------

    final_approval_rate = (
        sum(
            result["final_verifier_approved"]
            for result in results
        )
        / total
    )

    return {
        "total_cases": total,

        "verifier_detection_rate": (
            verifier_detection_rate
        ),

        "revision_success_rate": (
            revision_success_rate
        ),

        "final_approval_rate": (
            final_approval_rate
        ),
    }


# ============================================================
# Percentage formatting
# ============================================================

def format_percentage(
    value: float | None,
) -> str:

    if value is None:

        return "N/A"

    return f"{value * 100:.1f}%"


# ============================================================
# Save results
# ============================================================

def save_results(
    summary: dict,
    cases: list[dict],
) -> Path:

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    output_path = (
        RESULTS_DIR
        / f"adversarial_{timestamp}.json"
    )

    payload = {
        "evaluation_timestamp": timestamp,

        "evaluation_type": "adversarial",

        "metrics": summary,

        "cases": cases,
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            indent=2,
        )

    return output_path


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 70)
    print("AEROWATCH ADVERSARIAL EVALUATION")
    print("=" * 70)

    cases = get_adversarial_cases()

    print(
        f"\nLoaded {len(cases)} adversarial cases."
    )

    verifier = VerificationAgent()

    reviser = RevisionAgent()

    results: list[dict] = []

    for case in cases:

        result = evaluate_case(
            case=case,
            verifier=verifier,
            reviser=reviser,
        )

        results.append(result)

    summary = calculate_summary(
        results
    )

    # --------------------------------------------------------
    # Print summary
    # --------------------------------------------------------

    print()
    print()

    print("=" * 70)
    print("AEROWATCH ADVERSARIAL SUMMARY")
    print("=" * 70)

    print(
        f"\nTotal cases: "
        f"{summary['total_cases']}"
    )

    print(
        f"Verifier detection rate: "
        f"{format_percentage(summary['verifier_detection_rate'])}"
    )

    print(
        f"Revision success rate: "
        f"{format_percentage(summary['revision_success_rate'])}"
    )

    print(
        f"Final approval rate: "
        f"{format_percentage(summary['final_approval_rate'])}"
    )

    print()
    print("-" * 70)
    print("PER-CASE RESULTS")
    print("-" * 70)

    for result in results:

        status = (
            "PASS"
            if (
                result["verifier_rejected"]
                and result["revision_succeeded"]
                and result["final_verifier_approved"]
                and result["error"] is None
            )
            else "FAIL"
        )

        print(
            f"\n[{status}] "
            f"{result['case_name']}"
        )

        print(
            f"  Verifier rejected bad analysis: "
            f"{result['verifier_rejected']}"
        )

        print(
            f"  Revision attempted: "
            f"{result['revision_attempted']}"
        )

        print(
            f"  Revised schema valid: "
            f"{result['revision_valid']}"
        )

        print(
            f"  Revision succeeded: "
            f"{result['revision_succeeded']}"
        )

        print(
            f"  Final verifier approved: "
            f"{result['final_verifier_approved']}"
        )

        if result["error"]:

            print(
                f"  Error: "
                f"{result['error']}"
            )

        if result["revision_error"]:

            print(
                f"  Revision error: "
                f"{result['revision_error']}"
            )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    output_path = save_results(
        summary=summary,
        cases=results,
    )

    print()
    print("=" * 70)
    print("ADVERSARIAL RESULTS SAVED")
    print("=" * 70)

    print(output_path)

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    failed_cases = [
        result
        for result in results
        if not (
            result["verifier_rejected"]
            and result["revision_succeeded"]
            and result["final_verifier_approved"]
            and result["error"] is None
        )
    ]

    print()

    if failed_cases:

        print(
            f"Adversarial evaluation completed with "
            f"{len(failed_cases)} failing case(s)."
        )

    else:

        print(
            "ALL ADVERSARIAL CASES PASSED."
        )


if __name__ == "__main__":
    main()