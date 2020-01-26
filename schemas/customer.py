from ma import ma
from models.customer import CustomerModel
from models.summary import SummaryModel
from schemas.summary import SummarySchema


class CustomerSchema(ma.ModelSchema):
    summaries = ma.Nested(SummarySchema, many=True)

    class Meta:
        model = CustomerModel
        dump_only = ("id",)
        include_fk = True
