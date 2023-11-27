from .models import Item, Inventory
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect

# Register your models here.


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "store",
        "release",
        "total_count",
    )

    fields = (
        "name",
        "total_count",
        "staff",
        "created_at",
        "modified_at",
    )

    readonly_fields = (
        "total_count",
        "created_at",
        "modified_at",
        "staff",
    )

    search_fields = (
        "name",
    )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/inventory/change_list.html'

    list_display = (
        "id",
        "item",
        "classification",
        "unit_price",
        "quantity",
        "total_price",
        "created_at",
        "modified_at",
        "staff",
    )

    fields = (
        "item",
        "classification",
        "unit_price",
        "quantity",
        "total_price",
        "memo",
        "created_at",
        "modified_at",
        "staff",
    )

    readonly_fields = (
        "total_price",
        "created_at",
        "modified_at",
        "staff",
    )

    search_fields = (
        "name",
    )

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                if not obj.staff:
                    obj.staff = request.user
                obj.total_price = obj.quantity * obj.unit_price
                super().save_model(request, obj, form, change)

                if request.POST:
                    obj = Inventory.objects.get(pk=obj.id)

                    item = obj.item
                    if obj.classification == "STORE":
                        item.total_count += obj.quantity
                        item.store += obj.quantity
                        item.save(update_fields=["total_count", "store"])
                    if obj.classification == "RELEASE":
                        item.total_count -= obj.quantity
                        item.release += obj.quantity

                        if item.total_count < 0:
                            raise ValidationError("총 갯수보다 출고가 많습니다.")
                        item.save(update_fields=["total_count", "release"])

                    obj.inventoryhistory_set.create(
                        classification=obj.classification,
                        item=obj.item,
                        unit_price=obj.unit_price,
                        quantity=obj.quantity,
                        total_price=obj.total_price,
                        memo=obj.memo,
                        staff=request.user,
                    )
        except ValidationError as e:
            self.message_user(request, f"Error: {e}", level=messages.ERROR)
            return HttpResponseRedirect(request.path_info)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            with transaction.atomic():
                obj = Inventory.objects.get(pk=object_id)
                history = obj.inventoryhistory_set.last()
                response = super().change_view(request, object_id, form_url, extra_context)

                if request.POST:
                    obj.total_price = obj.quantity * obj.unit_price
                    obj.save(update_fields=["total_price"])

                    item = obj.item

                    if history.classification == "STORE":
                        item.total_count -= history.quantity
                        item.store -= history.quantity

                    if history.classification == "RELEASE":
                        item.total_count += history.quantity
                        item.release -= history.quantity

                    if item.total_count < 0:
                        print(item.total_count, "????")
                        raise ValidationError("총 갯수보다 출고가 많습니다.")

                    item.save(update_fields=["total_count", "store", "release"])

                    obj.inventoryhistory_set.create(
                        classification=obj.classification,
                        item=obj.item,
                        unit_price=obj.unit_price,
                        quantity=obj.quantity,
                        total_price=obj.total_price,
                        memo=obj.memo,
                        staff=request.user,
                    )

                return response
        except ValidationError as e:
            self.message_user(request, f"Error: {e}", level=messages.ERROR)
            return HttpResponseRedirect(request.path_info)

    @transaction.atomic
    def delete_view(self, request, object_id, extra_context=None):
        obj = Inventory.objects.get(pk=object_id)
        item = obj.item

        classification = obj.classification
        quantity = obj.quantity

        response = super().delete_view(request, object_id, extra_context)

        if response.status_code == 302:
            if classification == "STORE":
                item.total_count -= quantity
                item.store -= quantity

            if classification == "RELEASE":
                item.total_count += quantity
                item.release -= quantity

            item.save(update_fields=["total_count", "store", "release"])

        return response

    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}
        # 통계를 계산하고 원하는 통계 데이터를 extra_context에 추가.
        total_count = Inventory.objects.count()  # 예시로 모델의 전체 개수를 가져오는 통계를 생성

        extra_context["total_count"] = total_count  # 통계를 extra_context에 추가
        return super().changelist_view(request, extra_context=extra_context)

    # def get_urls(self):
    #     app_label = self.model._meta.app_label
    #     model_name = self.model._meta.model_name

    #     return [
    #         path(
    #             '<path:object_id>/manage_inventory_history/',
    #             self.admin_site.admin_view(self.manage_inventory_history_view),
    #             name=f'{app_label}_{model_name}_manage_inventory_history'
    #         ),
    #     ] + super().get_urls()

    # def manage_inventory_history_view(self, request, object_id, extra_context=None):
    #     # First check if the user can see this history.
    #     model = self.model
    #     obj = self.get_object(request, unquote(object_id))
    #     if obj is None:
    #         return self._get_obj_does_not_exist_redirect(
    #             request, model._meta, object_id
    #         )

    #     has_permission = self.has_view_or_change_permission(request, obj)

    #     if not has_permission:
    #         raise PermissionDenied

    #     # Then get the history for this object.
    #     opts = model._meta
    #     app_label = opts.app_label

    #     action_list = (
    #         InventoryHistory.objects
    #         .filter(inventory_id=object_id)
    #         .order_by('-id')
    #     )

    #     context = {
    #         **self.admin_site.each_context(request),
    #         'title': _('Change history: %s') % obj,
    #         'subtitle': None,
    #         'action_list': action_list,
    #         'module_name': str(capfirst(opts.verbose_name_plural)),
    #         'object': obj,
    #         'opts': opts,
    #         'preserved_filters': self.get_preserved_filters(request),
    #         **(extra_context or {}),
    #     }

    #     request.current_app = self.admin_site.name

    #     return TemplateResponse(request, self.object_history_template or [
    #         f"admin/{app_label}/{opts.model_name}/manage_inventory_history.html",
    #         f"admin/{app_label}/manage_inventory_history.html",
    #         "admin/manage_inventory_history.html",
    #     ], context)
