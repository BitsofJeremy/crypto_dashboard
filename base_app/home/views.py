from flask import Blueprint, render_template
from flask_login import login_required
import logging
import random

# Local imports
from base_app.data.models import Wallets
from base_app.utils import read_wallet

logger = logging.getLogger(__name__)

home = Blueprint('home', __name__)


# Basic site routes
@home.route('/')
def index():
    # Gets Wallets and Tokens from DB
    wallets = Wallets.query.order_by(Wallets.date_modified.desc()).all()
    print(wallets)
    wallet_list = []
    for wallet in wallets:
        w = read_wallet(_id=wallet.id)
        wallet_list.append(w)

    return render_template(
        'index.html',
        wallets=wallet_list,
    )


@home.route('/test')
@login_required
def test():
    # Just a test page that requires login
    secret_data = "This is a secret page" \
                  "Ideally we would update data from here"
    return render_template('test.html', secret_data=secret_data)
