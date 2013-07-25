# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

"""
@brief Main Java Generation module
"""

import pdb
import os
import shutil

import of_g
from loxi_ir import *
import lang_java

import loxi_utils.loxi_utils as loxi_utils

import java_gen.java_model as java_model

def gen_all_java(out, name):
    basedir='loxi_output/openflowj'
    srcdir = "%s/src/main/java/" % basedir
    print "Outputting to %s" % basedir
    if os.path.exists(basedir):
        shutil.rmtree(basedir)
    os.makedirs(basedir)
    copy_prewrite_tree(basedir)

    gen = JavaGenerator(srcdir)
    gen.create_of_interfaces()
    gen.create_of_classes()
    gen.create_of_const_enums()

    with open('README.java-lang') as readme_src:
        out.writelines(readme_src.readlines())
    out.close()


class JavaGenerator(object):
    templates_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

    def __init__(self, basedir):
        self.basedir = basedir
        self.java_model = java_model.model

    def render_class(self, clazz, template, **context):
        context['class_name'] = clazz.name
        context['package'] = clazz.package

        filename = os.path.join(self.basedir, "%s/%s.java" % (clazz.package.replace(".", "/"), clazz.name))
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        prefix = '//::(?=[ \t]|$)'
        print "filename: %s" % filename
        with open(filename, "w") as f:
            loxi_utils.render_template(f, template, [self.templates_dir], context, prefix=prefix)

    def create_of_const_enums(self):
        for enum in self.java_model.enums:
            if enum.name in ["OFPort"]:
                continue
            self.render_class(clazz=enum,
                    template='const.java', enum=enum, all_versions=self.java_model.versions)

    def create_of_interfaces(self):
        """ Create the base interfaces for of classes"""
        for interface in self.java_model.interfaces:
            #if not utils.class_is_message(interface.c_name):
            #    continue
            self.render_class(clazz=interface,
                    template="of_interface.java", msg=interface)

    def create_of_classes(self):
        """ Create the OF classes with implementations for each of the interfaces and versions """
        for interface in self.java_model.interfaces:
            if interface.name == "OFTableMod":
                continue
            if not loxi_utils.class_is_message(interface.c_name) and not loxi_utils.class_is_oxm(interface.c_name):
                continue
            for java_class in interface.versioned_classes:
                self.render_class(clazz=java_class,
                        template='of_class.java', version=java_class.version, msg=java_class,
                        impl_class=java_class.name)


def mkdir_p(path):
    """ Emulates `mkdir -p` """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def copy_file_with_boiler_plate(src_name, dst_name, with_boiler=True):
    with open("java_gen/pre-written/%s" % src_name, "r") as src:
        with open(dst_name, "w") as dst:
            if with_boiler:
                print_boiler_plate(os.path.basename(dst_name), dst)
            dst.writelines(src.readlines())

def frob(s, **kwargs):
    """ Step through string s and for each key in kwargs,
         replace $key with kwargs[key] in s.
    """
    for k,v in kwargs.iteritems():
        s = s.replace('$%s' % k, v)
    return s

def copy_prewrite_tree(basedir):
    """ Recursively copy the directory structure from ./java_gen/pre-write
       into $basedir"""
    print "Copying pre-written files into %s" % basedir
    #subprocess.call("cd java_gen/pre-written && tar cpf - pom.xml | ( cd ../../%s && tar xvpf - )" % basedir,
    #        shell=True)
    os.symlink(os.path.abspath("java_gen/pre-written/pom.xml"), "%s/pom.xml" % basedir)
