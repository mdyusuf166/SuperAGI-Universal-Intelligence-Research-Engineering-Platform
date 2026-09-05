class ScientificSafetyPolicy:
 forbidden=("physical experiment","lab execution","human subject","dangerous chemical","pathogen","clinical diagnosis","autonomous hardware")
 def assess(self,text):
  matches=[item for item in self.forbidden if item in text.casefold()]
  return {"allowed":not matches,"mode":"COMPUTATIONAL_PROPOSAL_ONLY","reasons":matches}
 def require_safe(self,text):
  decision=self.assess(text)
  if not decision["allowed"]: raise PermissionError("Scientific safety policy rejected unsafe or real-world execution request")
  return decision
