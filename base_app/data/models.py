# base_app/data/models.py

# Add random data to store here
from base_app import db
from base_app.auth.models import Base


# ## WALLETS ###
class Wallets(Base):
    """ Individual Wallet data """
    __tablename__ = 'wallets'

    """
    {
    "id": "Integer",  # created by DB
    "date_created": "datetime" # created by DB
    "date_modified": "datetime" # created by DB
    "wallet": "string",
    "wallet_address": "string",
    "token": "string",
    "network": "string",
    "current_price": "float",
    "base_stake": "float",
    "current_stake": "float",
    "current_awards": "float",
    "current_stake_value": current_stake * token_current_price,
    "current_awards_value": current_awards * token_current_price,
    }
    """

    wallet = db.Column(db.String)
    wallet_address = db.Column(db.String)

    # token info
    token = db.Column(db.String)
    network = db.Column(db.String)
    current_price = db.Column(db.Float)
    base_stake = db.Column(db.Float)

    # Current stats
    current_stake = db.Column(db.Float)
    current_awards = db.Column(db.Float)
    current_stake_value = db.Column(db.Float)
    current_awards_value = db.Column(db.Float)

    def __init__(self, wallet_address):
        self.wallet_address = wallet_address

    def __repr__(self):
        return f"{self.wallet_address} - {self.token} - {self.current_stake} - {self.current_stake_value}"

    def update(self, **kwargs):
        """ Updates a Wallet """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_current_price(self, _price):
        self.current_price = _price

    def update_base_stake(self, _stake):
        self.base_stake = _stake

    @property
    def serialize(self):
        """ Returns a dictionary of the token information """
        return {
            "id": self.id,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
            "wallet": self.wallet,
            "wallet_address": self.wallet_address,
            "token": self.token,
            "network": self.network,
            "current_price": self.current_price,
            "base_stake": self.base_stake,
            "current_stake": self.current_stake,
            "current_awards": self.current_awards,
            "current_stake_value": self.current_stake_value,
            "current_awards_value": self.current_awards_value,
        }

