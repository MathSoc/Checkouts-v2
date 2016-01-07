import wtforms
from models import User, Asset

class AssetForm(wtforms.Form):
    """
    Form for an asset.
    """
    name = wtforms.TextField('Name', (
        wtforms.validators.Length(max=100),
    ))
    
    total = wtforms.IntegerField('Total', (
        wtforms.validators.NumberRange(min=1),
    ))
    
    asset_type = wtforms.SelectField('Type', (
        wtforms.validators.AnyOf(dict(Asset.ASSET_TYPE).keys()),
    ), choices=Asset.ASSET_TYPE)

    owner = wtforms.SelectField('Club Owner', (
        wtforms.validators.AnyOf(dict(Asset.OWNER_TYPE).keys()),
    ), choices=Asset.OWNER_TYPE)

    created = wtforms.HiddenField('Created')

    def validate_name(form, field):
        """
        Validates that an asset with this name does not already exist.
        """
        if not form.created.data == 'False':
            if len(Asset.query.filter_by(name=field.data).all()) >= 1:
                raise wtforms.ValidationError('Asset name already exists.')

class UserForm(wtforms.Form):
    """
    Form for an user.
    """
    identifier = wtforms.TextField('Id', (
        wtforms.validators.Length(max=10),
    ))

    name = wtforms.TextField('Name', (
        wtforms.validators.Length(max=80),
    ))

    first_name = wtforms.TextField('First Name', (
        wtforms.validators.Length(max=80),
    ))

    last_name = wtforms.TextField('Last Name', (
        wtforms.validators.Length(max=80),
    ))

    membership = wtforms.SelectField('Membership', (
        wtforms.validators.AnyOf(dict(User.MEMBERSHIP_TYPE).keys()),
    ), choices=User.MEMBERSHIP_TYPE)

    refunded = wtforms.BooleanField('Refunded')

    created = wtforms.HiddenField('Created')

    def validate_identifier(form, field):
        """
        Validates that the combination of identifier and membership are
        unique.
        """
        identifier = field.data
        membership = form.membership.data
        if not form.created.data == 'False':
            exists = User.query.filter_by(identifier=identifier,
                                          membership=membership)
            if len(exists.all()) >= 1:
                raise wtforms.ValidationError('User already exists.')

    def validate_membership(form, field):
        """
        Validates that given the membership, the correct (name,
        first_name, last_name) combinations exist.
        """
        if field.data == 'club' or field.data == 'Club':
            if len(form.name.data) == 0:
                raise wtforms.ValidationError('Name must exist for club.')
        elif len(form.first_name.data) == 0:
            raise wtforms.ValidationError('Student must have a first name.')
        elif len(form.last_name.data) == 0:
            raise wtforms.ValidationError('Student must have a last name.')
