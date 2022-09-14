from drf_yasg.inspectors import SwaggerAutoSchema


class SwaggerExcludeParams(SwaggerAutoSchema):
    def get_query_parameters(self):
        return []


def custom_params_swagger_schema(*params) -> SwaggerAutoSchema:
    class SwaggerCustomParams(SwaggerAutoSchema):
        def get_query_parameters(self):
            return list(params)

    return SwaggerCustomParams
