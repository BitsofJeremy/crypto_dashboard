# base_app/api/views.py

from flask import Blueprint, g, jsonify
from flask_httpauth import HTTPTokenAuth
from flask_restx import Resource, Api, reqparse
import logging

# Local imports
from base_app import db
from base_app.auth.models import User
from base_app.data.models import Wallets
from base_app.utils import create_wallet, read_wallet, \
    update_wallet, delete_wallet

logger = logging.getLogger(__name__)


# Build API swagger auth into headers
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization'
    }
}

api_bp = Blueprint('api', __name__, url_prefix="/api/v1")
api = Api(api_bp,
          title="THE CRYPTO DASHBOARD API",
          contact="DEAFMICE",
          authorizations=authorizations,
          doc='/')

httpauth = HTTPTokenAuth(
    scheme='Bearer'
)
# API Namespaces
wallet_api_ns = api.namespace('wallets', description='Wallet operations')
auth_ns = api.namespace('auth', description='Authentication operations')


# Helper functions
@httpauth.verify_token
def verify_password(token):
    """ Uses the Bearer token to authenticate the user """
    # try to authenticate by token
    user = User.verify_auth_token(token)
    if not user:
        logger.info(user)
        logger.info("User is not user")
        return False
    g.user = user
    logger.info(f"{user} Sent and API request.")
    return True


# API Token refresh helper API route
@auth_ns.route('/renew')
class ApiToken(Resource):
    @api.doc(security='apikey')
    @httpauth.login_required
    def get(self):
        """
        Renews Current User's Token
        Returns: Token JSON
        """
        # Get current user from DB and renew the token
        user = User.query.filter(User.id == g.user.id).one()
        user.token = user.generate_auth_token()
        db.session.add(user)
        db.session.commit()
        token = g.user.token
        return jsonify({'token': token.decode('ascii')})


# ### Wallet API Routes ###
@wallet_api_ns.route('/all')
class WalletList(Resource):
    def get(self):
        """ GET a list of all wallets.
        ---
            - This endpoint returns all wallets in the DB

            Returns: JSON wallets
        """
        data_return = {"wallets": []}
        wallets = Wallets.query.order_by(Wallets.date_modified.desc()).all()
        for wallet in wallets:
            data_return['wallets'].append(wallet.serialize)
        return jsonify(data_return)


@wallet_api_ns.route('')
class WalletAPI(Resource):
    """ Provides Wallet API resources. """
    # ##### GET WALLET PARSER #####
    get_parser = reqparse.RequestParser()
    get_parser.add_argument(
        'wallet_id',
        type=int,
        required=True,
        help="Enter the wallet ID number."
    )

    # ##### POST WALLET PARSER #####
    post_parser = reqparse.RequestParser()
    # Required
    post_parser.add_argument(
        'wallet_address',
        type=str,
        required=True,
        help="REQUIRED - Enter the wallet address [example: 0x12345]"
    )

    # ##### PUT WALLET SPEC PARSER #####
    put_parser = reqparse.RequestParser()
    # Required
    put_parser.add_argument(
        'wallet_id',
        type=int,
        required=True,
        help="Enter the wallet ID to update."
    )
    put_parser.add_argument(
        'wallet',
        type=str,
        required=True,
        help="Update the wallet name [Example: J_wallet]"
    )
    put_parser.add_argument(
        'wallet_address',
        type=str,
        required=True,
        help="Update the wallet address [Example: 0x12345]"
    )
    put_parser.add_argument(
        'current_stake',
        type=float,
        required=True,
        help="Update the wallet current_stake [Example: 42.0]"
    )
    put_parser.add_argument(
        'current_awards',
        type=float,
        required=True,
        help="Update the wallet current_awards [Example: 0.042]"
    )

    # @api.doc(security='apikey')
    @wallet_api_ns.expect(get_parser)
    # @httpauth.login_required
    def get(self):
        """
        GET one wallet
        ---
            - Required: a wallet ID number
            - Returns one wallet in JSON format
        """
        data = WalletAPI.get_parser.parse_args()
        wallet_id = int(data['wallet_id'])
        wallet = read_wallet(wallet_id)
        if wallet:
            return jsonify(wallet)
        else:
            logger.warning(f"Sorry, Wallet ID: {wallet_id} Not Found")
            return {
                       "message": f"Sorry, Wallet ID: {wallet_id} Not Found"
                   }, 404

    # @api.doc(security='apikey')
    @wallet_api_ns.expect(post_parser)
    # @httpauth.login_required
    def post(self):
        """ POST a wallet
        ---
            - Requirements
                - A wallet spec requires the wallet address
            - Returns: wallet JSON
        """
        data = WalletAPI.post_parser.parse_args()
        logger.info(data)
        wallet_inst = create_wallet(**data)
        logger.info(wallet_inst)
        return {"wallet": f"{wallet_inst}"}, 201

    # @api.doc(security='apikey')
    # @httpauth.login_required
    @wallet_api_ns.expect(put_parser)
    def put(self):
        """ UPDATE a wallet
        ---
            - Updates: a wallet
            - Returns: wallet JSON
        """
        # get dictionary from parser
        data = WalletAPI.put_parser.parse_args()
        wallet_id = int(data['wallet_id'])
        logger.info('API Data PUT')
        logger.info(data)
        # Search for wallet by ID
        wallet_data = Wallets.query.filter_by(id=wallet_id).first()

        if wallet_data:
            wallet_inst = update_wallet(wallet_id, **data)
            if wallet_inst:
                logger.info(f"Updated Wallet {wallet_id} with new data")
                return {"message": f"Wallet {wallet_id} Updated"}, 201
            else:
                # Something went wrong, not sure if broken
                return {"message": f"Crap... {wallet_inst}"}, 501
        else:
            # NO WALLET FOUND IN DB
            # We kick back 401 as we want them to POST first
            logger.info(f"Wallet {wallet_id} not found")
            return {"message": "WALLET WAS NOT FOUND, SORRY."}, 401

    # @api.doc(security='apikey')
    @wallet_api_ns.expect(get_parser)
    # @httpauth.login_required
    def delete(self):
        """ DELETE a Wallet
        ---
            - Deletes a Wallet
            - Required: a Wallet ID
            - Returns: Happy message
        """
        data = WalletAPI.get_parser.parse_args()
        wallet_inst = delete_wallet(data['wallet_id'])

        if wallet_inst:
            logger.info(f"Deleted Wallet: {data['wallet_id']}")
            return {"message": f"{data['wallet_id']} Deleted"}
        else:
            logger.info("Something went wrong with delete.")
            logger.info("Check if wallet_id exists?")
            return {"message": "Something went wrong. "
                               "Missing wallet_id?"}, 404
