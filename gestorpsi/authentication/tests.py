# -*- coding: utf-8 -*-

"""
Copyright (C) 2008 GestorPsi

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

from django.db import models
from gestorpsi.person.models import Person
from gestorpsi.organization.models import Organization
from django.contrib.auth.models import User, UserManager, Group
from django.test import TestCase
from .models import Profile, Role

from django.test import TestCase, Client, RequestFactory
from django.core.urlresolvers import reverse
from gestorpsi.util.test_utils import setup_required_data

user_stub = {
    "address": u'niceaddress',
    "address_number": u'244',
    "city": u'1',
    "cpf": u'741.095.117-63',
    "email": u'user15555@gmail.com',
    "name": u'user15555',
    "organization": u'niceorg',
    "password1": u'nicepass123',
    "password2": u'nicepass123',
    "phone": u'(55) 5432-4321',
    "plan": u'1',
    "shortname": u'NICE',
    "state": u'1',
    "username": u'user15',
    "zipcode": u'12312-123',
}

bad_user_stub = {
    "address": u'niceaddress',
    "address_number": u'244',
    "city": u'1',
    "cpf": u'741.095.117-63',
    "email": u'user15555@gmail.com',
    "name": u'user15555',
    "organization": u'niceorg',
    "password1": u'nicepass123',
    "password2": u'nicepass1', # different pass
    "phone": u'(55) 5432-4321',
    "plan": u'1',
    "shortname": u'NICE',
    "state": u'1',
    "username": u'user15',
    "zipcode": u'12312-123',
}

class SignupTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        setup_required_data()

    def test_signup_should_work(self):
        response = self.client.get(reverse('registration-register'))
        self.assertEqual(response.status_code, 200)

    def test_signup_shouldnt_work_for_wrong_values(self):
        old_user_count = User.objects.count()
        response = self.client.post(reverse('registration-register'), bad_user_stub)
        self.assertEqual(User.objects.count(), old_user_count)

    def test_signup_with_correct_data_should_increase_total_number_of_users(self):
        old_user_count = User.objects.count()
        response = self.client.post(reverse('registration-register'), user_stub)
        self.assertEqual(User.objects.count(), old_user_count+1)

class SigninTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        user = User.objects.create_user(username=user_stub["name"], email="mytest@gmail.com", password="botafogo.com")
        user.profile = Profile()
        user.profile.save()
        user.save()

    def test_login_should_work(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

class ProfileTest(TestCase):
    def setUp(self):
        tobias = User()
        joaquim = Person()
        mcdonalds = Organization()

        self.perfil = Profile()
        self.perfil.user = tobias
        tobias.username = "Tobias"
        self.perfil.pk = 99
        mcdonalds.pk = 12
        joaquim.pk = 44
        self.perfil.org_active = mcdonalds
        self.perfil.person = joaquim
        self.perfil._set_temp("abacate")

    def test_user_is_set(self):
        self.assertIsInstance(self.perfil.user, User)

    def test_user_parms_are_avaible(self):
        self.assertIsNone(self.perfil.user.id)

    def test_organization_is_set(self):
        self.assertIsNotNone(self.perfil.organization)

    def test_try_login_is_set(self):
        self.assertFalse(self.perfil.try_login)

    def test_crypt_temp_is_set(self):
        self.assertIsNotNone(self.perfil.crypt_temp)

    def test_org_active_is_set(self):
        self.assertEquals(self.perfil.org_active_id, self.perfil.org_active.pk)

    def test_person_is_set(self):
        self.assertEquals(self.perfil.person_id, self.perfil.person.pk)

    def test_unicode(self):
        self.assertEquals(
            self.perfil.user.username, unicode(self.perfil))

    def test_set_temp(self):
        self.assertEquals(self.perfil.crypt_temp, "adf59a5eebcef0f8")

    def test_get_temp(self):
        self.assertEquals(self.perfil._get_temp(), "abacate")


class RoleTest(TestCase):

    def setUp(self):
        perfil = Profile()
        perfil.pk = 10
        tabajara = Organization()
        tabajara.pk = 555
        grupo = Group()
        grupo.pk = 19
        joao = User()
        joao.username = "Joao"
        perfil.user = joao
        tabajara.name = "zueira"
        grupo.name = "grupo1"
        self.papel = Role()
        self.papel.profile = perfil
        self.papel.organization = tabajara
        self.papel.group = grupo

    def test_profile_is_set(self):
        self.assertEquals(self.papel.profile_id, 10)

    def test_organization_is_set(self):
        self.assertEquals(self.papel.organization_id, 555)

    def test_group_is_set(self):
        self.assertEquals(self.papel.group_id, 19)

    def test_role_unicode(self):
        self.assertEquals(u"%s | %s | %s" % (
            self.papel.profile, self.papel.organization, self.papel.group), unicode(self.papel))
