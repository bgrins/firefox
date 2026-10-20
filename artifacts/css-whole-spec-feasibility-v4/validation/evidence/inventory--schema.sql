PRAGMA foreign_keys = ON;

CREATE TABLE document (
  id TEXT PRIMARY KEY,
  family TEXT NOT NULL,
  edition TEXT NOT NULL,
  url TEXT NOT NULL,
  sha256 TEXT NOT NULL CHECK(length(sha256) = 64),
  standing TEXT NOT NULL CHECK(standing IN ('active','draft','obsolete','experimental','unresolved')),
  UNIQUE(family, edition)
);

CREATE TABLE catalog_entry (
  id TEXT PRIMARY KEY,
  discovery_source TEXT NOT NULL,
  document_id TEXT REFERENCES document(id),
  disposition TEXT NOT NULL CHECK(disposition IN ('target','dependency','historical','non-normative','unresolved')),
  reason TEXT NOT NULL,
  reviewed INTEGER NOT NULL CHECK(reviewed IN (0,1))
);

CREATE TABLE profile (
  id TEXT PRIMARY KEY,
  scope TEXT NOT NULL CHECK(scope IN ('sample','synthetic-test','normative-universe')),
  revision TEXT NOT NULL,
  roles_json TEXT NOT NULL CHECK(json_valid(roles_json)),
  universe_review TEXT NOT NULL CHECK(universe_review IN ('open','accepted')),
  source_partition_review TEXT NOT NULL CHECK(source_partition_review IN ('open','accepted')),
  interaction_review TEXT NOT NULL CHECK(interaction_review IN ('open','accepted'))
);

CREATE TABLE profile_document (
  profile_id TEXT REFERENCES profile(id),
  document_id TEXT REFERENCES document(id),
  purpose TEXT NOT NULL CHECK(purpose IN ('active','dependency','historical')),
  PRIMARY KEY(profile_id, document_id)
);

CREATE TABLE source_unit (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL REFERENCES document(id),
  selector TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('prose','algorithm','grammar','table','figure','idl','metadata')),
  normative_context TEXT NOT NULL CHECK(normative_context IN ('normative','informative','role-dependent','unresolved')),
  disposition TEXT NOT NULL CHECK(disposition IN ('obligation','definition','informative','historical','unclassified')),
  span_json TEXT NOT NULL CHECK(json_valid(span_json)),
  reviewed INTEGER NOT NULL CHECK(reviewed IN (0,1))
);

CREATE TABLE semantic_interface (
  id TEXT PRIMARY KEY,
  revision TEXT NOT NULL,
  signature_json TEXT NOT NULL CHECK(json_valid(signature_json)),
  state TEXT NOT NULL CHECK(state IN ('proposed','accepted'))
);

CREATE TABLE predicate (
  id TEXT PRIMARY KEY,
  definition_ref TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('proposed','accepted'))
);

CREATE TABLE requirement (
  id TEXT PRIMARY KEY,
  revision TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('rule','provider','interaction','generic','authority')),
  modality TEXT NOT NULL CHECK(modality IN ('must','must-not','should','may','definition','role-dependent')),
  subject TEXT NOT NULL,
  guard_json TEXT NOT NULL CHECK(json_valid(guard_json)),
  contract_json TEXT NOT NULL CHECK(json_valid(contract_json)),
  interface_id TEXT REFERENCES semantic_interface(id),
  interpretation TEXT NOT NULL CHECK(interpretation IN ('candidate','accepted','conflict'))
);

CREATE TABLE requirement_source (
  requirement_id TEXT REFERENCES requirement(id),
  unit_id TEXT REFERENCES source_unit(id),
  PRIMARY KEY(requirement_id, unit_id)
);

CREATE TABLE target (
  profile_id TEXT REFERENCES profile(id),
  requirement_id TEXT REFERENCES requirement(id),
  disposition TEXT NOT NULL CHECK(disposition IN ('active','replaced','not-applicable','historical')),
  decision_ref TEXT NOT NULL,
  PRIMARY KEY(profile_id, requirement_id)
);

CREATE TABLE dependency (
  source_id TEXT REFERENCES requirement(id),
  target_id TEXT REFERENCES requirement(id),
  kind TEXT NOT NULL CHECK(kind IN ('semantic','provider','host','temporal','registry','premise')),
  PRIMARY KEY(source_id, target_id, kind)
);

CREATE TABLE choice_contract (
  requirement_id TEXT PRIMARY KEY REFERENCES requirement(id),
  allowed_relation_ref TEXT NOT NULL,
  constraint_refs_json TEXT NOT NULL CHECK(json_valid(constraint_refs_json)),
  persistence TEXT NOT NULL CHECK(persistence IN ('invocation','element','document','session','platform','specified-history')),
  consistency_obligation TEXT NOT NULL REFERENCES requirement(id),
  nonempty_obligation TEXT NOT NULL REFERENCES requirement(id)
);

CREATE TABLE transition_contract (
  requirement_id TEXT PRIMARY KEY REFERENCES requirement(id),
  trigger_refs_json TEXT NOT NULL CHECK(json_valid(trigger_refs_json)),
  observation_ref TEXT NOT NULL,
  timing_protocol_ref TEXT NOT NULL,
  readiness_obligation TEXT NOT NULL REFERENCES requirement(id)
);

CREATE TABLE replacement (
  profile_id TEXT REFERENCES profile(id),
  old_id TEXT REFERENCES requirement(id),
  new_id TEXT NOT NULL REFERENCES requirement(id),
  covered_guard_json TEXT NOT NULL CHECK(json_valid(covered_guard_json)),
  residual_guard_json TEXT NOT NULL CHECK(json_valid(residual_guard_json)),
  residual_id TEXT REFERENCES requirement(id),
  authority_ref TEXT NOT NULL,
  partition_review TEXT NOT NULL CHECK(partition_review IN ('open','accepted')),
  PRIMARY KEY(profile_id, old_id)
);

CREATE TABLE binding (
  profile_id TEXT REFERENCES profile(id),
  requirement_id TEXT REFERENCES requirement(id),
  level TEXT NOT NULL CHECK(level IN ('model','executable','native')),
  requirement_revision TEXT NOT NULL,
  contract_digest TEXT NOT NULL CHECK(length(contract_digest) = 64),
  interface_revision TEXT,
  artifact_ref TEXT NOT NULL,
  observation_ref TEXT NOT NULL,
  evidence_ref TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('open','unsupported','conditional','accepted','stale')),
  PRIMARY KEY(profile_id, requirement_id, level)
);
