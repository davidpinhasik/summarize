from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from models.customer import CustomerModel
from schemas.customer import CustomerSchema
from libs.strings import gettext


customer_schema = CustomerSchema()
customer_list_schema = CustomerSchema(many=True)


class Customer(Resource):  # we will change some of the methods from
    @classmethod
    # @jwt_required()
    def get(cls, email: str):
        customer = CustomerModel.find_by_email(email)

        if customer:
            return customer_schema.dump(customer), 200
        return {"message": gettext("CUSTOMER_NOT_FOUND")}, 404

    @classmethod
    # @jwt_required()  commented out just for testing purposes
    def post(cls, email: str):
        if CustomerModel.find_by_email(email):
            return {"message": gettext("CUSTOMER_EMAIL_ALREADY_EXISTS").format("email")}, 400,

        customer_json = request.get_json()
        print(f"customer_json={customer_json}")
        customer_json["email"] = email  # we must add this to json since we receive email from endpoint and not from
        # request body like the lname and fname

        customer = customer_schema.load(customer_json)

        # customer = CustomerModel(email=email)
        try:
            customer.save_to_db()
        except:
            return {"message": gettext("CUSTOMER_ERROR_INSERTING")}, 500

        return customer_schema.dump(customer), 201

    @classmethod
    # @jwt_required()  commented out just for testing purposes
    def delete(cls, email: str):
        customer = CustomerModel.find_by_email(email)
        if customer:
            customer.delete_from_db()
            return {"message": gettext("CUSTOMER_DELETED")}

        return {"message": gettext("CUSTOMER_NOT_FOUND")}, 404


class CustomerList(Resource):  # just for testing purposes
    @classmethod
    def get(cls):
        return {"customers": customer_list_schema.dump(CustomerModel.find_all())}, 200
