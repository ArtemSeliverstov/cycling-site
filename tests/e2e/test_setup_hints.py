"""The setup hint (issue #319), as a visitor and a member meet it."""

import pytest
from playwright.sync_api import Page, expect

from accounts.models import User
from tests.e2e.conftest import inject_session


@pytest.mark.django_db(transaction=True)
def test_a_visitor_is_asked_to_sign_in_and_cannot_wave_it_away(page: Page, live_server):
    page.goto(f"{live_server.url}/ru/calendar/list/")
    hint = page.locator("#setup-hint")
    expect(hint).to_be_visible()
    expect(hint.locator("form")).to_have_count(0)
    expect(hint.locator(".btn-close")).to_have_count(0)
    hint.locator("a.btn-primary").click()
    expect(page).to_have_url(f"{live_server.url}/ru/accounts/login/?next=%2Fru%2Fcalendar%2Flist%2F")


@pytest.mark.django_db(transaction=True)
def test_a_member_turns_one_reminder_off_and_meets_the_next(page: Page, live_server):
    member = User.objects.create_user(
        username="e2e_rider", email="e2e_rider@test.local", password="testpass123!", role=User.Role.PARTICIPANT
    )
    inject_session(page, live_server, member)
    page.goto(f"{live_server.url}/ru/calendar/list/")
    hint = page.locator("#setup-hint")
    expect(hint).to_have_attribute("data-hint", "preferences")

    # A dismissed confirmation keeps the reminder: closing it must be deliberate.
    page.once("dialog", lambda dialog: dialog.dismiss())
    hint.locator("button[type=submit]").click()
    expect(hint).to_have_attribute("data-hint", "preferences")

    page.once("dialog", lambda dialog: dialog.accept())
    hint.locator("button[type=submit]").click()
    expect(page.locator("#setup-hint")).to_have_attribute("data-hint", "registration_data")
