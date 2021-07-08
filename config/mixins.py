from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db import models
from django.forms import Select, Textarea
from django_currentuser.db.models import CurrentUserField
from rest_framework.serializers import ModelSerializer
from constance import config
from django.db.models.query import QuerySet
from django_currentuser.middleware import get_current_user, get_current_authenticated_user

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class BaseModelSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'created_by',
                            'updated_at', 'updated_by',)


class MultiFieldSortableChangeList(ChangeList):
    def get_ordering(self, request, queryset):
        ORDER_VAR = admin.views.main.ORDER_VAR
        params = self.params
        ordering = list(self.model_admin.get_ordering(
            request) or self._get_default_ordering())

        if ORDER_VAR in params:
            ordering = []
            order_params = params[ORDER_VAR].split('.')
            for p in order_params:
                try:
                    none, pfx, idx = p.rpartition('-')
                    field_name = self.list_display[int(idx)]
                    order_fields = self.get_ordering_field(field_name)

                    if type(order_fields) == str:
                        order_fields = [order_fields]

                    for order_field in order_fields:
                        if order_field:
                            ordering.append(pfx + order_field)
                except (IndexError, ValueError):
                    continue

        ordering.extend(queryset.query.order_by)

        pk_name = self.lookup_opts.pk.name
        if not (set(ordering) & set(['pk', '-pk', pk_name, '-' + pk_name])):
            ordering.append('-pk')

        return ordering


class BaseModel(models.Model):
    created_by = CurrentUserField(related_name='%(class)s_created_by')
    updated_by = CurrentUserField(on_update=True, related_name='%(class)s_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EventosManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.all_obj = kwargs.pop('all_obj', False)
        super(EventosManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        from django.db.models import Q
        current_user = get_current_user()
        if self.all_obj:
            return QuerySet(self.model)
        elif self.model.__name__ not in ('Certificados', 'Transmissor'):
            if current_user and not current_user.is_superuser and config.FILTER_BY_USER:
                return QuerySet(self.model).filter(created_by_id=current_user.id)
            return QuerySet(self.model)
        else:
            if current_user and not current_user.is_superuser and config.FILTER_BY_USER:
                return QuerySet(self.model).filter(Q(created_by_id=current_user.id)|Q(users__id=current_user.id))
            return QuerySet(self.model)


class BaseModelEsocial(models.Model):
    created_by = CurrentUserField(related_name='%(class)s_created_by_esocial')
    updated_by = CurrentUserField(on_update=True, related_name='%(class)s_updated_by_esocial')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = EventosManager()
    all_objects = EventosManager(all_obj=True)

    class Meta:
        abstract = True


class BaseModelReinf(models.Model):
    created_by = CurrentUserField(related_name='%(class)s_created_by_reinf')
    updated_by = CurrentUserField(on_update=True, related_name='%(class)s_updated_by_reinf')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = EventosManager()

    class Meta:
        abstract = True


class AuditoriaManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.all_obj = kwargs.pop('all_obj', True)
        super(AuditoriaManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        from django.db.models import Q
        current_user = get_current_user()
        if self.all_obj:
            return super().get_queryset()
        elif self.model.__name__ not in ('Certificados', 'Transmissor'):
            if current_user and not current_user.has_perm('auth.view_user') and config.FILTER_BY_USER:
                return super().get_queryset().filter(created_by=current_user)
            return super().get_queryset()
        else:
            if current_user and not current_user.has_perm('auth.view_user') and config.FILTER_BY_USER:
                return super().get_queryset().filter(Q(created_by=current_user)|Q(users__id=current_user.id))
            return super().get_queryset()


class AuditoriaAdminEventos(admin.ModelAdmin):
    objects = AuditoriaManager()

    def has_view_permission(self, request, obj=None):
        current_user = get_current_user()
        if current_user and not current_user.has_perm('auth.view_user') and config.FILTER_BY_USER and \
            obj and obj.created_by != current_user:
            return False
        return super().has_view_permission(request)

    def get_queryset(self, request):
        from django.db.models import Q
        current_user = get_current_user()
        queryset = super().get_queryset(request)
        if current_user and not current_user.has_perm('auth.view_user') and config.FILTER_BY_USER:
            if self.model.__name__ in ('Certificados', 'Transmissor'):
                return queryset.filter(Q(created_by=current_user)|Q(users__id=current_user.id))
            else:
                return queryset.filter(created_by=current_user)
        return queryset

    readonly_fields = (
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
    )

    def get_readonly_fields(self, request, obj=None):
        if self.model.__name__ in ('Certificados', 'Transmissor'):
            if request.user.has_perm('auth.view_user'):
                return super(AuditoriaAdminEventos, self).get_readonly_fields(request, obj)
            else:
                return self.readonly_fields + ('users',)
        else:
            return super(AuditoriaAdminEventos, self).get_readonly_fields(request, obj)


class AuditoriaAdmin(admin.ModelAdmin):
    readonly_fields = (
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
    )


class AuditoriaAdminInline(admin.TabularInline):
    readonly_fields = AuditoriaAdmin.readonly_fields
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={
                'rows': 4,
                'cols': 40
            })
        },
        models.ForeignKey: {
            'widget': Select(attrs={
                'style': 'width:150px'
            })
        },
    }


class AuditoriaAdminStackedInlineInline(admin.StackedInline):
    readonly_fields = AuditoriaAdmin.readonly_fields
