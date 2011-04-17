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

import reversion
from django.db import models
from django.utils.translation import ugettext as _
from gestorpsi.organization.models import Organization, Agreement, AgeGroup, EducationLevel, HierarchicalLevel, Procedure
from gestorpsi.careprofessional.models import CareProfessional, Profession
from gestorpsi.client.models import Client
from gestorpsi.util.uuid_field import UuidField 

class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ['name']

class Modality(models.Model):
    name= models.CharField(max_length=100)
    
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ['name']

class Area(models.Model):
    area_name = models.CharField(_('Area Name'), max_length=100, blank=True, null=True)
    area_code = models.CharField(_('Area Code'), max_length=30, blank=True, null=True)
    service_type = models.ManyToManyField(ServiceType, null=True, blank=True)
    modalities = models.ManyToManyField(Modality, null=True, blank=True)
    age_group = models.ManyToManyField(AgeGroup, null=True, blank=True)
    education_level = models.ManyToManyField(EducationLevel, null=True, blank=True)
    hierarchical_level = models.ManyToManyField(HierarchicalLevel, null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.area_name

    class Meta:
        ordering = ['area_name']

class ServiceManager(models.Manager):
    def active(self):
        return super(ServiceManager, self).get_query_set().filter(active=True)
    def deactive(self):
        return super(ServiceManager, self).get_query_set().filter(active=False)

class Service(models.Model):
    """
    This class is used to maintain information on services.
    @author: Gestorpsi
    @version: 1.0
    """
    id = UuidField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=999, blank=True)
    keywords = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    is_group = models.BooleanField(default=False)
    area = models.ForeignKey(Area)
    service_type = models.ForeignKey(ServiceType)
    modalities = models.ManyToManyField(Modality)
    
    age_group = models.ManyToManyField(AgeGroup, null=True, blank=True)
    education_level = models.ManyToManyField(EducationLevel, null=True, blank=True)
    hierarchical_level = models.ManyToManyField(HierarchicalLevel, null=True, blank=True)
    
    agreements= models.ManyToManyField(Agreement)
    professions = models.ManyToManyField(Profession)
    research_project = models.BooleanField(default=False) 
    research_project_name = models.CharField(max_length=500)
    organization = models.ForeignKey(Organization, null=True)
    responsibles = models.ManyToManyField( CareProfessional, related_name="resp_services" )
    professionals = models.ManyToManyField( CareProfessional, related_name="prof_services" )
    css_color_class = models.IntegerField(max_length=2, blank=True, null=True, default=0)
    date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)
    academic_related = models.BooleanField(_('Academic (supervised) related service'), default=False)
    is_online = models.BooleanField(default=False)
    procedures = models.ManyToManyField(Procedure)
    
    objects = ServiceManager()

    def __unicode__(self):
        u = u"%s" % (self.name)
        if self.is_group:
            u += " (%s)" % _('Group')
        return u
    
    def _name_html(self):
        return u"<div class='service_name_html color%s'>&nbsp;</div> %s" % (self.css_color_class, self.name)
    name_html = property(_name_html)

    def _name_html_inline(self):
        return u"%s <div class='service_name_html_inline color%s'>&nbsp;</div>" % (self.name, self.css_color_class)
    name_html_inline = property(_name_html_inline)

    class Meta:
        ordering = ['name']
        get_latest_by = ['date']

    def revision(self):
        return reversion.models.Version.objects.get_for_object(self).order_by('-revision__date_created').latest('revision__date_created').revision

class ServiceGroup(models.Model):
    id = UuidField(primary_key=True)
    service = models.ForeignKey(Service, null=False, blank=False)
    members = models.ManyToManyField(Client, null=True, blank=True, through='GroupMembers')
    description = models.CharField(max_length=100)
    comments = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return u'%s' % (self.description)

    class Meta:
        ordering = ['-active', 'service__name', 'description']

    def charged_members(self):
        from gestorpsi.referral.models import ReferralDischarge
        members = []
        for i in self.groupmembers_set.all():
            if not ReferralDischarge.objects.filter(client=i.client, referral=i.referral):
                members.append(i)
        return members

    def revision(self):
        return reversion.models.Version.objects.get_for_object(self).order_by('-revision__date_created').latest('revision__date_created').revision

class GroupMembers(models.Model):
    group = models.ForeignKey(ServiceGroup)
    client = models.ForeignKey(Client)
    referral = models.ForeignKey('referral.Referral')
    
    def __unicode__(self):
        return u'%s' % (self.client)

reversion.register(Service)
reversion.register(Modality)
reversion.register(Agreement)
