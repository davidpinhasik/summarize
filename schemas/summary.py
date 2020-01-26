from ma import ma
from models.summary import SummaryModel
from models.customer import CustomerModel

class SummarySchema(ma.ModelSchema):
    class Meta:
        model = SummaryModel
        load_only = ("customer", "user",)
        dump_only = ("id", "created_dt","audio_file_name", "text", "user_id")
        include_fk = True
