import inspect
from app.schemas.job import JobSearchQuery
from app.services.job_scraper import JobSpySource, job_service


def test_jobspy_dependency_import_and_signature():
    from jobspy import scrape_jobs
    assert callable(scrape_jobs)
    sig = inspect.signature(scrape_jobs)
    assert "site_name" in sig.parameters
    assert "search_term" in sig.parameters
    assert "results_wanted" in sig.parameters


def test_jobspy_source_execution():
    source = JobSpySource()
    query = JobSearchQuery(role="Software Engineer", location="Bengaluru", limit=2)
    raw_jobs, statuses = source.search(query)
    assert isinstance(statuses, dict)
    assert "indeed" in statuses or "linkedin" in statuses or "fallback_board" in statuses
    assert isinstance(raw_jobs, list)
