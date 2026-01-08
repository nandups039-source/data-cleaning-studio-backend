from rest_framework import serializers

class DocumentSerializer(serializers.Serializer):
    doc_id = serializers.CharField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Document ID is required.",
            "blank": "Document ID cannot be blank.",
            "null": "Document ID is required."
        }
    )
    type = serializers.CharField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Type is required.",
            "blank": "Type cannot be blank.",
            "null": "Type is required."
        }
    )
    counterparty = serializers.CharField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Counterparty is required.",
            "blank": "Counterparty cannot be blank.",
            "null": "Counterparty is required."
        }
    )
    project = serializers.CharField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Project is required.",
            "blank": "Project cannot be blank.",
            "null": "Project is required."
        }
    )
    expiry_date = serializers.DateField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Expiry Date is required.",
            "invalid": "Expiry Date is invalid.",
            "null": "Expiry Date is required."
        }
    )
    amount = serializers.FloatField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Amount is required.",
            "invalid": "Amount must be a number.",
            "null": "Amount is required."
        }
    )
