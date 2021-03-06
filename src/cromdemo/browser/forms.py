# -*- coding: utf-8 -*-

import uuid
from crom import target, order
from cromlech.browser import IURL
from cromlech.browser.exceptions import HTTPFound
from cromlech.browser.interfaces import IPublicationRoot
from cromlech.browser.directives import title
from cromlech.security import permissions
from dolmen.message import send
from dolmen.forms.base import Fields, FAILURE
from dolmen.forms.base import action, name, context, form_component
from dolmen.forms.base import apply_data_event
from dolmen.forms.base.errors import Error
from zope.lifecycleevent import created, added

from . import ITab, Form
from ..auth import Auth
from ..models import Leaf, ILeaf, ILogin


@form_component
@name('add.leaf')
@context(IPublicationRoot)
@target(ITab)
@order(50)
@title("Add a leaf")
@permissions('Manage')
class AddLeaf(Form):

    fields = Fields(ILeaf)
    ignoreContent = True

    @action('Add')
    def add(self):
        data, errors = self.extractData()
        if errors:
            self.errors = errors
            return FAILURE

        uid = str(uuid.uuid4().hex)  # a simple UUID id to avoid conflict.
        content = Leaf(data['title'], data['body'])
        created(content)
        self.context[uid] = content
        added(content, newParent=self.context, newName=uid)
        raise HTTPFound(IURL(self.context, self.request))


@form_component
@name('edit')
@context(ILeaf)
@target(ITab)
@order(20)
@title("Edit the content")
@permissions('Manage')
class Edit(Form):

    fields = Fields(ILeaf)
    ignoreContent = False

    @action('Apply')
    def apply(self):
        data, errors = self.extractData()
        if errors:
            self.errors = errors
            return FAILURE

        content = self.getContent()
        apply_data_event(self.fields, content, data)
        raise HTTPFound(IURL(content, self.request))


@form_component
@name('login')
@context(Auth)
class Login(Form):

    fields = Fields(ILogin)
    ignoreContent = True

    @property
    def action_url(self):
        return self.request.url

    @action('Log me')
    def login(self):
        data, errors = self.extractData()
        if errors:
            self.errors = errors
            return FAILURE

        success = self.context.authenticate(
            data['username'], data['password'])
        if not success:
            self.errors.append(Error(
                title='Login failed',
                identifier=self.prefix,
            ))
            return FAILURE

        send('Login successful.')
        raise HTTPFound(self.request.url)
