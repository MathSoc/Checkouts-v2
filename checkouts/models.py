from sqlalchemy_utils import ChoiceType
from checkouts import db
import utils

class Checkout(db.Model):
    """
    A Checkout model corresponds to a relationship between a user and
    an asset that the user has checked out.  A user may check out an
    asset more than one time or multiple of the same asset.
    """
    _id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user._id'))
    asset_id = db.Column(db.Integer, db.ForeignKey('asset._id'))

    # Check-in and check-out status of the asset for the user.
    checkout_time = db.Column(db.Integer, default=utils.current_time)
    checkin_time = db.Column(db.Integer, nullable=True)

    @property
    def checkin_date(self):
        timestamp = utils.timestamp_to_local(self.checkin_time)
        return timestamp.strftime('%B %d %Y %I:%M %p')

    @property
    def checkout_date(self):
        timestamp = utils.timestamp_to_local(self.checkout_time)
        return timestamp.strftime('%B %d %Y %I:%M %p')

    @property
    def asset(self):
        return Asset.query.filter_by(_id=self.asset_id)[0]

    @property
    def user(self):
        return User.query.filter_by(_id=self.user_id)[0]

    @property
    def returned(self):
        return self.checkin_time is not None

    @property
    def total_time(self):
        """
        Returns the total time this item has been checked out in
        seconds.
        """
        if self.checkin_time is not None:
            return (self.checkin_time - self.checkout_time)
        return (utils.current_time() - self.checkout_time)

    def __repr__(self):
        return '<Checkout %r> %r' % (self.user.full_name,
                                     self.asset.name)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Asset(db.Model):
    ASSET_TYPE = (
        ('book', 'Book'),
        ('board', 'Board Game'),
        ('other', 'Other'),
    )

    OWNER_TYPE = (
        ('mathsoc', 'MathSoc'),
        ('watsfic', 'Watsfic'),
    )

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    asset_type = db.Column(ChoiceType(ASSET_TYPE))
    owner = db.Column(ChoiceType(OWNER_TYPE))

    # Keeps track of how many the given asset are in total in
    # inventory.  This is different than stock, which is how many we
    # have left.
    total = db.Column(db.Integer)

    # A one-to-many relationship between a checkout and an asset.  A
    # checkout contains the user that has checked out this asset.
    checkouts = db.relationship('Checkout',
                                backref=db.backref('asset'),
                                lazy='dynamic')

    # We want the type of asset and the name of said asset to be
    # unique together.
    __table_args__ = (
        db.UniqueConstraint('name', 'asset_type', name='_name_type_uc'),
    )

    @property
    def out(self):
        return self.checkouts.filter(Checkout.checkin_time == None)

    @property
    def stock(self):
        return self.total - self.out.count()

    def __repr__(self):
        return '<Asset %r> %r' % (self.asset_type.value.title(),
                                  self.name)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class User(db.Model):
    MEMBERSHIP_TYPE = (
        ('watsfic', 'Watsfic'),
        ('general', 'General'),
        ('club', 'Club'),
    )

    _id = db.Column(db.Integer, primary_key=True)

    # Identifiers for the user.  Either name or the pair (first_name,
    # last_name) should not be NULL.
    identifier = db.Column(db.String(10))
    name = db.Column(db.String(80), nullable=True)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)

    # Is true if the user has refunded there MathSoc fee.
    refunded = db.Column(db.Boolean, default=False)

    # The type of membership the user checking out assets is.  This
    # can be general for a student, or can be a club or WatsFic.
    membership = db.Column(ChoiceType(MEMBERSHIP_TYPE))

    # A one-to-many relationship between a checkout and an user.  A
    # checkout contains the asset that the user has checked out.
    checkouts = db.relationship('Checkout',
                                backref=db.backref('borrowee'),
                                lazy='dynamic')

    # Specifies a unique constraint for the pair of (membership,
    # identifier); in this case, we want to ensure that student
    # numbers are only used once, and membership identifiers are only
    # used once for a particular club/WatsFic.
    __table_args__ = (
        db.UniqueConstraint('identifier',
                            'membership',
                            name='_user_membership_uc'),
    )

    @property
    def is_student(self):
        return self.membership.code in ['general', 'watsfic']

    @property
    def full_name(self):
        if not self.is_student:
            return self.name
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def open_checkouts(self):
        return self.checkouts.filter(Checkout.checkin_time == None)

    def __repr__(self):
        return '<%r %r>' % (self.membership.value.title(),
                            self.full_name)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
