from stack_nav import *
from database import *

def settings_badge_store(state):
    return selection({
        ("API: %s" % get("badge_store.url", "http://badgeserver.emfcamp.org/2018")): change_database_string("Set API", "badge_store.url", "http://badgeserver.emfcamp.org/2018"),
        ("Repo: %s" % get("badge_store.repo", "emfcamp/Mk4-Apps")): change_database_string("Git repository", "badge_store.repo", "emfcamp/Mk4-Apps"),
        ("Ref: %s" % get("badge_store.ref", "master")): change_database_string("Set branch, tag or commit", "badge_store.ref", "master")
    }, "Badge store settings")
