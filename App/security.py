from functools import wraps

from flask import flash, redirect, request, session, url_for
from flask_login import current_user

SESSION_2FA_VERIFIED_KEY = "two_factor_verified"


def clear_2fa_verified():
    session.pop(SESSION_2FA_VERIFIED_KEY, None)


def mark_2fa_verified():
    session[SESSION_2FA_VERIFIED_KEY] = True


def is_2fa_verified_for_session():
    return session.get(SESSION_2FA_VERIFIED_KEY) is True


def two_factor_verified_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not (current_user and getattr(current_user, "is_authenticated", False)):
            return redirect(url_for("accounts.login", next=request.path))

        if not getattr(current_user, "is_two_factor_authentication_enabled", False):
            flash(
                "You must enable 2-Factor Authentication before accessing Shorty tables.",
                "info",
            )
            return redirect(url_for("accounts.setup_two_factor_auth"))

        if not is_2fa_verified_for_session():
            flash("Please complete 2-Factor Authentication verification.", "info")
            return redirect(url_for("accounts.verify_two_factor_auth"))

        return view_func(*args, **kwargs)

    return wrapped
