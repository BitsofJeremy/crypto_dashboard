# Putting simple helper utility functions here

import arrow
from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps
import logging
logger = logging.getLogger(__name__)

# Local imports
from base_app import db
from base_app.data.models import Wallets
from base_app.auth.models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash("You are not allowed to access that resource", 403)
                return redirect(url_for('home.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.DASHBOARD_ADMINS)(f)


def get_time():
    """ Gets time and returns a dictionary with formatted time """
    utc = arrow.utcnow()
    local = utc.to('US/Pacific')
    # Get UNIX Epoc
    post_time = local.timestamp
    # Get human time
    display_time = local.format('YYYY-MM-DD HH:mm')
    time_dict = {'post_time': post_time, 'display_time': display_time}
    return time_dict


# ### WALLETS ####
def create_wallet(**kwargs):
    # print(kwargs)
    task = {
        "wallet_address": kwargs["wallet_address"],
    }
    wallet_inst = Wallets(**task)
    db.session.add(wallet_inst)
    db.session.commit()
    return wallet_inst.serialize


def read_wallet(_id):
    wallet_inst = Wallets.query.filter_by(id=_id).first()
    return wallet_inst.serialize


def update_wallet(_id, **kwargs):
    wallet_inst = Wallets.query.filter_by(id=_id).first()
    wallet_inst.update(**kwargs)
    db.session.commit()
    return wallet_inst.serialize


def delete_wallet(_id):
    wallet_inst = Wallets.query.filter_by(id=_id).first()
    db.session.delete(wallet_inst)
    db.session.commit()
    return True
