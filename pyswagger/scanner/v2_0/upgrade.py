from __future__ import absolute_import
from ...scan import Dispatcher
from ...errs import SchemaError
from ...utils import jp_split
from ...spec.v2_0.objects import (
    Swagger,
    Info,
    Contact,
    License,
    PathItem,
    Operation,
    Parameter,
    Items,
    Response,
    Header,
    Tag,
    Schema,
    XMLObject,
    SecurityScheme,
    )
from ...spec.v3_0 import objects


def _convert_to_request_body(obj, path):
    pass


def _convert_to_parameter(obj, path):
    ret = {}

    # optional fields
    if obj.description:
        ret['description'] = obj.description
    if obj.required is not None:
        ret['required'] = obj.required

    """ note for convert from 'collectionFormat' to 3.0's 'style' and 'explode'
    - collectionFormat:csv -> style:form
    - collectionFormat:ssv -> style:spaceDelimited
    - collectionFormat:pipes -> style:pipeDelimited
    - collectionFormat:tsv -> ? (github issue raised)
    - collectionFormat:multi -> explode
    """

    ret['name'] = obj.name

    # 'in' field
    in_ = getatr(obj, 'in')
    # TODO: convert to style, schema, explode, or content
    if in_ == 'query':
    elif in_ == 'header':
    elif in_ == 'path':
    elif in_ == 'formData':
    else:
        raise SchemaError('unknown "in" property: {}, {}'.format(in_, path))

def _convert_response(obj, path, status):
    pass



class Upgrade(object):
    """ convert 2.0 object to 3.0 object
    """
    class Disp(Dispatcher): pass

    def __init__(self):
        self.openapi = None
        self.info = None
        self.contact = None
        self.license = None
        self.paths = {}


    @Disp.register([Swagger])
    def _swagger(self, path, obj, app):
        self.openapi = {
            'openapi': obj.swagger,
        }

    @Disp.register([Info])
    def _info(self, path, obj, app):
        self.info = {
            'title': obj.title,
            'description': obj.description,
            'termsOfService': obj.termsOfService,
            'version': obj.version,
        }

    @Disp.register([Contact])
    def _contact(self, path, obj, app):
        self.contact = {
            'name': obj.name,
            'url': obj.url,
            'email': obj.email,
        }

    @Disp.register([License])
    def _license(self, path, obj, app):
        self.license = {
            'name': obj.name,
            'url': obj.url,
        }

    @Disp.register([PathItem])
    def _path_item(self, path, obj, app):
        # key to parent object
        pkey = jp_split(path)[2]

        # according to spec, a path item might still be empty,
        # so we need to make sure its existence here.
        self.paths.setdefault(pkey, {})

    @Disp.register([Operation])
    def _operation(self, path, obj, app):
        # key to parent object
        tokens = jp_split(path)
        pkey, op = tokens[2], tokens[3]

        target = self.paths[pkey].setdefault(op, {})
        # optional fields
        if obj.tags:
            target['tags'] = obj.tags
        if obj.summary:
            target['summary'] = obj.summary
        if obj.description:
            target['description'] = obj.description
        # TODO: externalDocs
        if obj.operationId:
            target['operationId'] = obj.operationId
        # TODO: consumes, produces, schemes
        if obj.parameters:
            ps = target.setdefault('parameters')
            for p in obj.parameters:
                in_ = getattr(p, 'in')
                if in_ == 'body' or (in_ == 'formData' and getattr(p, 'type') == 'file'):
                    target['requestBody'] = _convert_to_request_body(p, path)
                else:
                    ps.append(_convert_to_parameter(p, path))
        if obj.deprecated is not None:
            target['deprecated'] = obj.deprecated
        if obj.security:
            target['security'] = obj.security

        # required fields
        rs = target.setdefault('responses', {})
        for k, r in six.iteritems(obj.responses):
            rs[k] = _convert_response(r, path, k)

