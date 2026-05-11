# =========================================================
# FILE:
# oic_doc_generator/models/service_model.py
# =========================================================

class ServiceModel:

    def __init__(
        self,
        endpoint="",
        request_elements=None,
        response_elements=None
    ):

        self.endpoint = endpoint

        self.request_elements = (
            request_elements
            if request_elements is not None
            else []
        )

        self.response_elements = (
            response_elements
            if response_elements is not None
            else []
        )

    # =====================================================
    # TO DICT
    # =====================================================

    def to_dict(self):

        return {

            "endpoint":
                self.endpoint,

            "request_elements":
                self.request_elements,

            "response_elements":
                self.response_elements
        }

    # =====================================================
    # HAS REQUEST
    # =====================================================

    def has_request(self):

        return (
            len(
                self.request_elements
            ) > 0
        )

    # =====================================================
    # HAS RESPONSE
    # =====================================================

    def has_response(self):

        return (
            len(
                self.response_elements
            ) > 0
        )

    # =====================================================
    # WRAPPER TYPE
    # =====================================================

    def get_wrapper_type(self):

        has_request = self.has_request()

        has_response = self.has_response()

        if (
            has_request
            and
            has_response
        ):

            return "Request/Response"

        if has_request:

            return "Request"

        if has_response:

            return "Response"

        return "Unknown"