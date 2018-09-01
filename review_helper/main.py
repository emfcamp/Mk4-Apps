"""Helps to test incoming PRs"""

___name___         = "PR Review Helper"
___license___      = "MIT"
___categories___   = ["System"]
___dependencies___ = ["dialogs", "app", "ugfx_helper", "badge_store", "http", "stack_nav", "wifi"]

import ugfx_helper, ugfx, wifi
from app import *
from dialogs import *
from stack_nav import *
from lib.badge_store import BadgeStore

title = "PR Review Helper"

def install(state):
    apps = set()
    with WaitingMessage(title="Fetching apps", text="Please wait...") as message:
        for category, a in state["store"].get_all_apps().items():
            apps.update(a)

    menu_items = [{"title": a, "app": a} for a in apps]

    option = prompt_option(menu_items, none_text="Back", title="title")

    if option:
        state["app"] = option
        return show_app

def show_app(state):
    a = state["app"]["app"]
    with WaitingMessage(title="Installing %s" % a, text="Please wait...") as message:
        apps_to_install = []#[a.name for a in get_apps()]
        apps_to_install.append(a)
        print(apps_to_install)
        installers = state["store"].install(apps_to_install)
        n = len(installers)
        for i, installer in enumerate(installers):
            message.text = "%s (%s/%s)" % (installer.path, i + 1, n)
            installer.download()

    notice("App %s has been successfully installed" % a, title=title, close_text="Run it!")
    App(a).boot()

def entry_point(state):
    url = database.get("badge_store.url", "http://badgeserver.emfcamp.org/2018")
    repo = database.get("badge_store.repo", "emfcamp/Mk4-Apps")
    store = BadgeStore(url=url, repo=repo)

    prs = store.get_prs()
    selection = prompt_option(prs, text="Select PR", none_text="Exit", title=title)
    if selection:
       state["store"] = BadgeStore(url=url, repo=repo, ref=selection["ref"])
       return install


### ENTRY POINT ###
ugfx_helper.init()
wifi.connect(show_wait_message=True)
nav(entry_point)
app.restart_to_default()
