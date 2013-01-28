#!/usr/bin/env python
#
#  prestans, a standards based WSGI compliant REST framework for Python
#  http://prestans.googlecode.com
#
#  Copyright (c) 2013, Eternity Technologies Pty Ltd.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#      * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#      * Neither the name of Eternity Technologies nor the
#        names of its contributors may be used to endorse or promote products
#        derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL ETERNITY TECHNOLOGIES BE LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

## @package prestans.tools.templates.closure.filter Google Closure templates for prestans filters
#

extension = "js"

template = """/*
 * Automatically generated by preplate
 */
 <%!
    from prestans.types import CONSTANT
%>

goog.provide('${namespace}.${name}');

goog.require('goog.json');
goog.require('goog.object');

goog.require('prestans.types.Filter');

<%

    dependencies = list()
    for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:

        full_path = None
        if is_array and model != "String" and model != "Integer" and model != "Float" and model != "Boolean" and model != "DateTime" and model != CONSTANT.ARRAY_DYNAMIC_ELEMENT_TEMPLATE:
            full_path = namespace+"."+model
        elif is_model:
            full_path = namespace+"."+model

        if full_path is not None and full_path not in dependencies:
            dependencies.append(full_path)
%>

% for dependency in dependencies:
goog.require('${dependency}');
%endfor

/**
 * @constructor
*/
${namespace}.${name} = function(opt_defaultValue) {

    if(opt_defaultValue != false)
        opt_defaultValue = true;

% for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:
%if is_model:
    this.${ccif}_ = new ${namespace}.${model}(opt_defaultValue);
%elif is_array and not (model == "String" or model == "Integer" or model == "Float" or model == "Boolean" or model == "DateTime" or model == CONSTANT.ARRAY_DYNAMIC_ELEMENT_TEMPLATE):
    this.${ccif}_ = new ${namespace}.${model}(opt_defaultValue);
%elif is_array and model == CONSTANT.ARRAY_DYNAMIC_ELEMENT_TEMPLATE:
    this.${ccif}_ = null;
%else:
    this.${ccif}_ = opt_defaultValue;
%endif
% endfor
};
goog.inherits(${namespace}.${name}, prestans.types.Filter);


% for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:
${namespace}.${name}.prototype.${ccif}_ = null;
% endfor


% for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:

%if model != CONSTANT.ARRAY_DYNAMIC_ELEMENT_TEMPLATE:
${namespace}.${name}.prototype.enable${cc} = function() {
%if is_model:
    this.${ccif}_ = new ${namespace}.${model}(true);
%elif is_array and not (model == "String" or model == "Integer" or model == "Float" or model == "Boolean" or model == "DateTime"):
    this.${ccif}_ = new ${namespace}.${model}(true);
%else:
	this.${ccif}_ = true;
%endif
};
%endif
% endfor

% for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:

%if model != CONSTANT.ARRAY_DYNAMIC_ELEMENT_TEMPLATE:
${namespace}.${name}.prototype.disable${cc} = function() {
%if is_model:
    this.${ccif}_ = new ${namespace}.${model}(false);
%elif is_array and not (model == "String" or model == "Integer" or model == "Float" or model == "Boolean" or model == "DateTime"):
    this.${ccif}_ = new ${namespace}.${model}(false);
%else:
	this.${ccif}_ = false;
%endif
};
%endif

% endfor

% for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:
${namespace}.${name}.prototype.get${cc} = function() {
    return this.${ccif}_;
};
% endfor

% for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:
%if is_model:
${namespace}.${name}.prototype.set${cc} = function(${ccif}) {
    if(${ccif} instanceof ${namespace}.${model})
        this.${ccif}_ = ${ccif};
    else
        throw "${ccif} must be of type ${namespace}.${model}";
};
%elif is_array and model == CONSTANT.ARRAY_DYNAMIC_ELEMENT_TEMPLATE:
${namespace}.${name}.prototype.set${cc} = function(${ccif}) {
    if(${ccif} instanceof prestans.types.Filter)
        this.${ccif}_ = ${ccif};
    else
        throw "${ccif} must be of type prestans.types.Filter";
};
%elif is_array and not (model == "String" or model == "Integer" or model == "Float" or model == "Boolean" or model == "DateTime"):
${namespace}.${name}.prototype.set${cc} = function(${ccif}) {
    if(${ccif} instanceof ${namespace}.${model})
        this.${ccif}_ = ${ccif};
    else
        throw "${ccif} must be of type ${namespace}.${model}";
};
%endif
% endfor

<%
attribute_string = ""
for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:
    if is_model:
        attribute_string += "this.%s_.anyFieldsEnabled() || " % ccif
    elif is_array and not (model == "String" or model == "Integer" or model == "Float" or model == "Boolean" or model == "DateTime"):
        attribute_string += "this.%s_.anyFieldsEnabled() || " % ccif
    else:
        attribute_string += "this.%s_ || " % ccif
attribute_string = attribute_string[:-4]
%>

${namespace}.${name}.prototype.anyFieldsEnabled = function() {
    return (${attribute_string});
};

${namespace}.${name}.prototype.getJSONObject = function(opt_complete) {

    if(opt_complete != true)
        opt_complete = false;

    var jsonifiedObject_ = {};
    
% for ud, cc, ccif, is_model, is_array, model, required, min_length, max_length, minimum, maximum, choices, format, default in attributes:
%if is_model:
    if(this.${ccif}_ != null && !goog.object.isEmpty(this.${ccif}_.getJSONObject(opt_complete)))
        jsonifiedObject_["${ud}"] = this.${ccif}_.getJSONObject(opt_complete);
    else if(opt_complete)
        jsonifiedObject_["${ud}"] = false;
%elif is_array and not (model == "String" or model == "Integer" or model == "Float" or model == "Boolean" or model == "DateTime"):
    if(this.${ccif}_ instanceof prestans.types.Filter && opt_complete)
        jsonifiedObject_["${ud}"] = this.${ccif}_.getJSONObject(opt_complete);
    else if(this.${ccif}_ instanceof prestans.types.Filter && !opt_complete && this.${ccif}_.anyFieldsEnabled())
        jsonifiedObject_["${ud}"] = this.${ccif}_.getJSONObject();
    else if(opt_complete)
        jsonifiedObject_["${ud}"] = false;
%else:
    if(this.${ccif}_ || opt_complete)
	   jsonifiedObject_["${ud}"] = this.${ccif}_;
%endif

%endfor

	return jsonifiedObject_;
};

${namespace}.${name}.prototype.getJSONString = function(opt_complete) {

    if(opt_complete != true)
        opt_complete = false;

    return goog.json.serialize(this.getJSONObject(opt_complete));
};

"""