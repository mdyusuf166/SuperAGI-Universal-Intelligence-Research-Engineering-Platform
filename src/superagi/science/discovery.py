from .models import CrossDomainResearchPlan
def cross_domain_plan(domains, contributions=None, dependencies=None): return CrossDomainResearchPlan(domains=list(domains), contributions=contributions or {}, dependencies=dependencies or [])
