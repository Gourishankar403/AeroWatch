from dataclasses import dataclass, field

from app.agents.verification_agent import VerificationAgent
from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment


@dataclass
class EvaluationResult:
    """
    Stores the evaluation result for one test case.
    """

    case_name: str

    # --------------------------------------------------------
    # Schema
    # --------------------------------------------------------

    schema_valid: bool = False

    # --------------------------------------------------------
    # Expected / actual evidence interpretation
    # --------------------------------------------------------

    expected_disruption: bool = False
    actual_disruption: bool = False
    disruption_correct: bool = False

    expected_weather_risk: bool = False
    actual_weather_risk: bool = False
    weather_risk_correct: bool = False

    # --------------------------------------------------------
    # Grounding
    # --------------------------------------------------------

    unsupported_claims: list[str] = field(
        default_factory=list
    )

    causation_violation: bool = False

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    verifier_approved: bool = False

    verification_issues: list[str] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Revision
    # --------------------------------------------------------

    revision_required: bool = False
    revision_succeeded: bool = False

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    final_approved: bool = False

    # --------------------------------------------------------
    # Errors
    # --------------------------------------------------------

    error: str | None = None


@dataclass
class EvaluationSummary:
    """
    Aggregated metrics across an evaluation suite.

    A metric can be None when the relevant capability was
    not exercised by the current evaluation suite.
    """

    total_cases: int

    schema_validity_rate: float

    disruption_accuracy: float

    weather_risk_accuracy: float

    causation_violation_rate: float

    verifier_detection_rate: float | None

    revision_success_rate: float | None

    final_approval_rate: float | None

    total_unsupported_claims: int

    cases: list[EvaluationResult] = field(
        default_factory=list
    )


# ============================================================
# Analysis evaluation
# ============================================================

def evaluate_analysis(
    analysis: AnalysisAssessment,
    operations: OperationsAssessment,
    weather: WeatherAssessment,
    expected_disruption: bool,
    expected_weather_risk: bool,
) -> EvaluationResult:
    """
    Evaluate one generated AnalysisAssessment against
    deterministic evidence and expected outcomes.
    """

    result = EvaluationResult(
        case_name="",
        schema_valid=True,
        expected_disruption=expected_disruption,
        actual_disruption=operations.disruption_detected,
        expected_weather_risk=expected_weather_risk,
        actual_weather_risk=weather.weather_risk_detected,
    )

    result.disruption_correct = (
        result.actual_disruption
        == result.expected_disruption
    )

    result.weather_risk_correct = (
        result.actual_weather_risk
        == result.expected_weather_risk
    )

    result.unsupported_claims = detect_unsupported_claims(
        analysis=analysis,
        operations=operations,
        weather=weather,
    )

    result.causation_violation = (
        detect_causation_violation(analysis)
    )

    return result


# ============================================================
# Unsupported claim detection
# ============================================================

def detect_unsupported_claims(
    analysis: AnalysisAssessment,
    operations: OperationsAssessment,
    weather: WeatherAssessment,
) -> list[str]:
    """
    Detect obvious claims that conflict with deterministic
    evidence.

    This detector is intentionally conservative.
    """

    claims: list[str] = []

    text = analysis.overall_assessment.lower()

    # --------------------------------------------------------
    # Operational disruption
    # --------------------------------------------------------

    if not operations.disruption_detected:

        positive_disruption_patterns = [
            "operational disruption is occurring",
            "an operational disruption is occurring",
            "airport disruption is occurring",
            "the airport is disrupted",
            "operations are disrupted",
            "operationally disrupted",
            "experiencing disruption",
            "undergoing disruption",
            "significant delays are occurring",
            "flight delays are occurring",
            "ground delay is active",
            "ground stop is active",
        ]

        negative_patterns = [
            "no operational disruption",
            "no evidence of an operational disruption",
            "no active operational disruption",
            "no airport disruption",
            "no evidence of an airport disruption",
            "no disruption is occurring",
            "no disruption detected",
            "does not indicate an operational disruption",
            "does not indicate an airport disruption",
            "without an operational disruption",
            "without operational disruption",
            "no faa operational disruption",
            "no faa operational event",
            "no evidence of an faa operational disruption",
        ]

        has_negative_context = any(
            pattern in text
            for pattern in negative_patterns
        )

        has_positive_claim = any(
            pattern in text
            for pattern in positive_disruption_patterns
        )

        if has_positive_claim and not has_negative_context:
            claims.append(
                "Unsupported operational disruption claim."
            )

    # --------------------------------------------------------
    # Weather risk
    # --------------------------------------------------------

    if not weather.weather_risk_detected:

        weather_risk_patterns = [
            "high weather risk",
            "severe weather risk",
            "significant weather risk",
            "elevated weather risk",
            "dangerous weather conditions",
            "high operational risk",
            "elevated operational risk",
        ]

        if any(
            pattern in text
            for pattern in weather_risk_patterns
        ):
            claims.append(
                "Unsupported weather-risk claim."
            )

    return claims


# ============================================================
# Causation detection
# ============================================================

def detect_causation_violation(
    analysis: AnalysisAssessment,
) -> bool:
    """
    Detect explicit claims that weather caused an operational
    disruption without supporting causal evidence.

    Generic phrases such as "due to IFR conditions" are not
    sufficient because they may simply explain the weather
    assessment rather than attribute the airport disruption
    to weather.
    """

    text = analysis.overall_assessment.lower()

    causal_patterns = [
        "weather caused",
        "weather conditions caused",
        "weather directly caused",
        "poor weather caused",
        "bad weather caused",
        "low visibility caused",
        "strong winds caused",
        "wind caused",
        "storm caused",
        "thunderstorms caused",
        "fog caused",
        "weather resulted in",
        "weather led to",
        "weather was responsible for",
        "weather is responsible for",
        "weather directly resulted in",
        "weather directly led to",
        "the disruption was caused by weather",
        "the disruption was caused by the weather",
        "the operational disruption was caused by weather",
        "the operational disruption was caused by the weather",
        "the delay was caused by weather",
        "the delay was caused by the weather",
        "the ground delay was caused by weather",
        "the ground delay was caused by the weather",
        "the disruption resulted from weather",
        "the disruption resulted from the weather",
        "the operational disruption resulted from weather",
        "the operational disruption resulted from the weather",
        "the disruption was due to weather",
        "the disruption was due to the weather",
        "the operational disruption was due to weather",
        "the operational disruption was due to the weather",
        "the delay was due to weather",
        "the delay was due to the weather",
        "the ground delay was due to weather",
        "the ground delay was due to the weather",
    ]

    return any(
        pattern in text
        for pattern in causal_patterns
    )


# ============================================================
# Verification evaluation
# ============================================================

def evaluate_verification(
    operations: OperationsAssessment,
    weather: WeatherAssessment,
    analysis: AnalysisAssessment,
) -> tuple[bool, list[str]]:
    """
    Run the deterministic VerificationAgent.
    """

    verifier = VerificationAgent()

    verification = verifier.verify(
        operations=operations,
        weather=weather,
        analysis=analysis,
    )

    return (
        verification.approved,
        verification.issues,
    )


# ============================================================
# Aggregate metrics
# ============================================================

def calculate_summary(
    results: list[EvaluationResult],
) -> EvaluationSummary:
    """
    Calculate aggregate evaluation metrics.

    Revision and verifier-detection metrics are None when
    the relevant capability was not exercised.
    """

    total_cases = len(results)

    if total_cases == 0:
        return EvaluationSummary(
            total_cases=0,
            schema_validity_rate=0.0,
            disruption_accuracy=0.0,
            weather_risk_accuracy=0.0,
            causation_violation_rate=0.0,
            verifier_detection_rate=None,
            revision_success_rate=None,
            final_approval_rate=None,
            total_unsupported_claims=0,
            cases=[],
        )

    # --------------------------------------------------------
    # Schema validity
    # --------------------------------------------------------

    schema_valid_count = sum(
        result.schema_valid
        for result in results
    )

    schema_validity_rate = (
        schema_valid_count / total_cases
    )

    # --------------------------------------------------------
    # Disruption interpretation accuracy
    # --------------------------------------------------------

    disruption_correct_count = sum(
        result.disruption_correct
        for result in results
    )

    disruption_accuracy = (
        disruption_correct_count / total_cases
    )

    # --------------------------------------------------------
    # Weather-risk interpretation accuracy
    # --------------------------------------------------------

    weather_correct_count = sum(
        result.weather_risk_correct
        for result in results
    )

    weather_risk_accuracy = (
        weather_correct_count / total_cases
    )

    # --------------------------------------------------------
    # Causation violations
    # --------------------------------------------------------

    causation_violation_count = sum(
        result.causation_violation
        for result in results
    )

    causation_violation_rate = (
        causation_violation_count / total_cases
    )

    # --------------------------------------------------------
    # Verifier detection
    # --------------------------------------------------------

    verification_targets = [
        result
        for result in results
        if (
            result.unsupported_claims
            or result.causation_violation
        )
    ]

    if verification_targets:

        detected_count = sum(
            not result.verifier_approved
            for result in verification_targets
        )

        verifier_detection_rate = (
            detected_count
            / len(verification_targets)
        )

    else:

        verifier_detection_rate = None

    # --------------------------------------------------------
    # Revision success
    # --------------------------------------------------------

    revision_cases = [
        result
        for result in results
        if result.revision_required
    ]

    if revision_cases:

        revision_success_count = sum(
            result.revision_succeeded
            for result in revision_cases
        )

        revision_success_rate = (
            revision_success_count
            / len(revision_cases)
        )

    else:

        revision_success_rate = None

    # --------------------------------------------------------
    # Final approval
    # --------------------------------------------------------

    final_approval_cases = [
        result
        for result in results
        if (
            result.verifier_approved
            or result.revision_required
        )
    ]

    if final_approval_cases:

        final_approval_count = sum(
            result.final_approved
            for result in final_approval_cases
        )

        final_approval_rate = (
            final_approval_count
            / len(final_approval_cases)
        )

    else:

        final_approval_rate = None

    # --------------------------------------------------------
    # Unsupported claims
    # --------------------------------------------------------

    total_unsupported_claims = sum(
        len(result.unsupported_claims)
        for result in results
    )

    return EvaluationSummary(
        total_cases=total_cases,
        schema_validity_rate=schema_validity_rate,
        disruption_accuracy=disruption_accuracy,
        weather_risk_accuracy=weather_risk_accuracy,
        causation_violation_rate=causation_violation_rate,
        verifier_detection_rate=verifier_detection_rate,
        revision_success_rate=revision_success_rate,
        final_approval_rate=final_approval_rate,
        total_unsupported_claims=total_unsupported_claims,
        cases=results,
    )


# ============================================================
# Formatting
# ============================================================

def format_percentage(
    value: float | None,
) -> str:
    """
    Convert a decimal metric into a human-readable percentage.

    None means the metric was not exercised.
    """

    if value is None:
        return "N/A"

    return f"{value * 100:.1f}%"