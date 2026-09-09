import json
from datetime import datetime, timezone
from pathlib import Path

from app.agents.analysis_agent import AnalysisAgent
from app.agents.verification_agent import VerificationAgent
from app.models.analysis import AnalysisAssessment

from scripts.evaluation.test_cases import EvaluationCase
from scripts.evaluation.test_cases import get_evaluation_cases

from scripts.evaluation.metrics import EvaluationResult
from scripts.evaluation.metrics import calculate_summary
from scripts.evaluation.metrics import detect_causation_violation
from scripts.evaluation.metrics import detect_unsupported_claims
from scripts.evaluation.metrics import format_percentage


RESULTS_DIR = (
    Path(__file__).resolve().parent / "results"
)


# ============================================================
# Single-case evaluation
# ============================================================

def evaluate_case(
    case: EvaluationCase,
    analysis_agent: AnalysisAgent,
    verification_agent: VerificationAgent,
) -> EvaluationResult:

    print()
    print("=" * 70)
    print(f"EVALUATING: {case.name}")
    print("=" * 70)

    print(case.description)

    result = EvaluationResult(
        case_name=case.name,
        expected_disruption=case.expected_disruption,
        expected_weather_risk=case.expected_weather_risk,
    )

    try:

        # ----------------------------------------------------
        # Analysis
        # ----------------------------------------------------

        print("\nRunning AnalysisAgent...")

        analysis = analysis_agent.analyze(
            operations=case.operations,
            weather=case.weather,
        )

        # ----------------------------------------------------
        # Schema validation
        # ----------------------------------------------------

        try:

            validated_analysis = (
                AnalysisAssessment.model_validate(
                    analysis
                )
            )

            result.schema_valid = True

        except Exception as error:

            result.schema_valid = False

            result.error = (
                "Analysis schema validation failed: "
                f"{error}"
            )

            return result

        # ----------------------------------------------------
        # Structured model outputs
        # ----------------------------------------------------

        result.actual_disruption = (
            validated_analysis.disruption_detected
        )

        result.actual_weather_risk = (
            validated_analysis.weather_risk_detected
        )

        # ----------------------------------------------------
        # Compare model output with expected state
        # ----------------------------------------------------

        result.disruption_correct = (
            result.actual_disruption
            == case.expected_disruption
        )

        result.weather_risk_correct = (
            result.actual_weather_risk
            == case.expected_weather_risk
        )

        # ----------------------------------------------------
        # Grounding checks
        # ----------------------------------------------------

        result.unsupported_claims = (
            detect_unsupported_claims(
                analysis=validated_analysis,
                operations=case.operations,
                weather=case.weather,
            )
        )

        result.causation_violation = (
            detect_causation_violation(
                validated_analysis
            )
        )

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        print("Running VerificationAgent...")

        verification = verification_agent.verify(
            operations=case.operations,
            weather=case.weather,
            analysis=validated_analysis,
        )

        result.verifier_approved = (
            verification.approved
        )

        result.verification_issues = (
            verification.issues
        )

        # ----------------------------------------------------
        # Final approval
        # ----------------------------------------------------

        result.final_approved = (
            verification.approved
        )

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        print("\nAnalysis:")
        print(
            validated_analysis.overall_assessment
        )

        print(
            f"\nConfidence: "
            f"{validated_analysis.confidence}"
        )

        print(
            f"Structured disruption_detected: "
            f"{validated_analysis.disruption_detected}"
        )

        print(
            f"Structured weather_risk_detected: "
            f"{validated_analysis.weather_risk_detected}"
        )

        print(
            f"Expected disruption: "
            f"{case.expected_disruption}"
        )

        print(
            f"Expected weather risk: "
            f"{case.expected_weather_risk}"
        )

        print(
            f"Schema valid: "
            f"{result.schema_valid}"
        )

        print(
            f"Disruption interpretation correct: "
            f"{result.disruption_correct}"
        )

        print(
            f"Weather-risk interpretation correct: "
            f"{result.weather_risk_correct}"
        )

        print(
            f"Unsupported claims: "
            f"{len(result.unsupported_claims)}"
        )

        print(
            f"Causation violation: "
            f"{result.causation_violation}"
        )

        print(
            f"Verification approved: "
            f"{result.verifier_approved}"
        )

        if result.verification_issues:

            print("\nVerification issues:")

            for issue in result.verification_issues:
                print(f"- {issue}")

        return result

    except Exception as error:

        result.error = str(error)

        print(
            f"\nERROR while evaluating "
            f"{case.name}: {error}"
        )

        return result


# ============================================================
# Summary display
# ============================================================

def print_summary(summary) -> None:

    print()
    print()
    print("=" * 70)
    print("AEROWATCH EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"\nTotal cases: "
        f"{summary.total_cases}"
    )

    print(
        f"Schema validity: "
        f"{format_percentage(summary.schema_validity_rate)}"
    )

    print(
        f"Disruption interpretation accuracy: "
        f"{format_percentage(summary.disruption_accuracy)}"
    )

    print(
        f"Weather-risk interpretation accuracy: "
        f"{format_percentage(summary.weather_risk_accuracy)}"
    )

    print(
        f"Causation violation rate: "
        f"{format_percentage(summary.causation_violation_rate)}"
    )

    print(
        f"Verifier detection rate: "
        f"{format_percentage(summary.verifier_detection_rate)}"
    )

    print(
        f"Revision success rate: "
        f"{format_percentage(summary.revision_success_rate)}"
    )

    print(
        f"Final approval rate: "
        f"{format_percentage(summary.final_approval_rate)}"
    )

    print(
        f"Total unsupported claims: "
        f"{summary.total_unsupported_claims}"
    )

    print()
    print("-" * 70)
    print("PER-CASE RESULTS")
    print("-" * 70)

    for case in summary.cases:

        status = (
            "PASS"
            if (
                case.schema_valid
                and case.disruption_correct
                and case.weather_risk_correct
                and not case.unsupported_claims
                and not case.causation_violation
                and case.verifier_approved
                and case.error is None
            )
            else "FAIL"
        )

        print(
            f"\n[{status}] "
            f"{case.case_name}"
        )

        print(
            f"  Schema valid: "
            f"{case.schema_valid}"
        )

        print(
            f"  Expected disruption: "
            f"{case.expected_disruption}"
        )

        print(
            f"  Actual disruption: "
            f"{case.actual_disruption}"
        )

        print(
            f"  Disruption interpretation: "
            f"{case.disruption_correct}"
        )

        print(
            f"  Expected weather risk: "
            f"{case.expected_weather_risk}"
        )

        print(
            f"  Actual weather risk: "
            f"{case.actual_weather_risk}"
        )

        print(
            f"  Weather-risk interpretation: "
            f"{case.weather_risk_correct}"
        )

        print(
            f"  Unsupported claims: "
            f"{len(case.unsupported_claims)}"
        )

        print(
            f"  Causation violation: "
            f"{case.causation_violation}"
        )

        print(
            f"  Verification approved: "
            f"{case.verifier_approved}"
        )

        if case.error:

            print(
                f"  Error: "
                f"{case.error}"
            )


# ============================================================
# JSON persistence
# ============================================================

def save_results(summary) -> Path:

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
        / f"evaluation_{timestamp}.json"
    )

    payload = {
        "evaluation_timestamp": timestamp,

        "total_cases": summary.total_cases,

        "metrics": {
            "schema_validity_rate": (
                summary.schema_validity_rate
            ),

            "disruption_accuracy": (
                summary.disruption_accuracy
            ),

            "weather_risk_accuracy": (
                summary.weather_risk_accuracy
            ),

            "causation_violation_rate": (
                summary.causation_violation_rate
            ),

            "verifier_detection_rate": (
                summary.verifier_detection_rate
            ),

            "revision_success_rate": (
                summary.revision_success_rate
            ),

            "final_approval_rate": (
                summary.final_approval_rate
            ),

            "total_unsupported_claims": (
                summary.total_unsupported_claims
            ),
        },

        "cases": [
            {
                "case_name": case.case_name,

                "schema_valid": (
                    case.schema_valid
                ),

                "expected_disruption": (
                    case.expected_disruption
                ),

                "actual_disruption": (
                    case.actual_disruption
                ),

                "disruption_correct": (
                    case.disruption_correct
                ),

                "expected_weather_risk": (
                    case.expected_weather_risk
                ),

                "actual_weather_risk": (
                    case.actual_weather_risk
                ),

                "weather_risk_correct": (
                    case.weather_risk_correct
                ),

                "unsupported_claims": (
                    case.unsupported_claims
                ),

                "causation_violation": (
                    case.causation_violation
                ),

                "verifier_approved": (
                    case.verifier_approved
                ),

                "verification_issues": (
                    case.verification_issues
                ),

                "revision_required": (
                    case.revision_required
                ),

                "revision_succeeded": (
                    case.revision_succeeded
                ),

                "final_approved": (
                    case.final_approved
                ),

                "error": case.error,
            }

            for case in summary.cases
        ],
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
    print("AEROWATCH CONTROLLED EVALUATION")
    print("=" * 70)

    cases = get_evaluation_cases()

    print(
        f"\nLoaded {len(cases)} evaluation cases."
    )

    analysis_agent = AnalysisAgent()

    verification_agent = VerificationAgent()

    results: list[EvaluationResult] = []

    for case in cases:

        result = evaluate_case(
            case=case,
            analysis_agent=analysis_agent,
            verification_agent=verification_agent,
        )

        results.append(result)

    summary = calculate_summary(
        results
    )

    print_summary(summary)

    output_path = save_results(
        summary
    )

    print()
    print("=" * 70)
    print("EVALUATION RESULTS SAVED")
    print("=" * 70)

    print(output_path)

    failed_cases = [
        case
        for case in results
        if (
            not case.schema_valid
            or not case.disruption_correct
            or not case.weather_risk_correct
            or case.unsupported_claims
            or case.causation_violation
            or not case.verifier_approved
            or case.error is not None
        )
    ]

    print()

    if failed_cases:

        print(
            f"Evaluation completed with "
            f"{len(failed_cases)} failing case(s)."
        )

    else:

        print(
            "ALL CONTROLLED EVALUATION CASES PASSED."
        )


if __name__ == "__main__":
    main()