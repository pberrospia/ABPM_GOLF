from app.services.abpm_analysis import ABPMAnalyzer, ABPMMetrics


def test_normotension_classification():
    metrics = ABPMMetrics(
        systolic_24h=120,
        diastolic_24h=75,
        systolic_day=125,
        diastolic_day=78,
        systolic_night=110,
        diastolic_night=65,
        measurements_total=90,
        measurements_day=40,
        measurements_night=20,
    )
    summary = ABPMAnalyzer(metrics).classify()
    assert summary.classification == "Normotensión según guías ESC/ESH 2023"
    assert summary.adequacy == "Adecuado"
    assert summary.dipping_pattern == "dipper"


def test_hypertension_detection_and_adequacy_warning():
    metrics = ABPMMetrics(
        systolic_24h=138,
        diastolic_24h=86,
        systolic_day=140,
        diastolic_day=90,
        systolic_night=130,
        diastolic_night=82,
        measurements_total=60,
        measurements_day=10,
        measurements_night=5,
    )
    summary = ABPMAnalyzer(metrics).classify()
    assert "Hipertensión sostenida" in summary.classification
    assert "Hipertensión diurna" in summary.classification
    assert "Hipertensión nocturna" in summary.classification
    assert "total: insuficiente" in summary.adequacy
    assert summary.pulse_pressure_24h == 52
