from django.db import models
from django.conf import settings


class Item(models.Model):
    """품목
    """

    class Meta:
        verbose_name = "품목"
        verbose_name_plural = "품목"

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="관리자",
        on_delete=models.SET_NULL,
        null=True,
    )

    name = models.CharField(
        verbose_name="품목명",
        null=False,
        blank=False,
        max_length=255,
        unique=True,
    )

    store = models.BigIntegerField(
        verbose_name="입고",
        default=0,
    )

    release = models.BigIntegerField(
        verbose_name="출고",
        default=0,
    )

    total_count = models.BigIntegerField(
        verbose_name="총 갯수",
        default=0,
    )

    created_at = models.DateTimeField(
        verbose_name="생성일",
        auto_now_add=True,
    )
    modified_at = models.DateTimeField(
        verbose_name="마지막으로 수정된 날짜",
        auto_now=True,
    )

    def __str__(self):
        return self.name


class Inventory(models.Model):
    """재고
    """

    class Meta:
        verbose_name = "재고"
        verbose_name_plural = "재고"

    classification = models.CharField(
        verbose_name="구분",
        max_length=40,
        choices=(
            ("STORE", "입고"),
            ("RELEASE", "출고"),
        ),
        blank=True,
    )

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="관리자",
        on_delete=models.SET_NULL,
        null=True,
    )

    item = models.ForeignKey(
        Item,
        verbose_name="품목",
        on_delete=models.SET_NULL,
        null=True
    )

    unit_price = models.BigIntegerField(
        verbose_name="단가",
    )

    quantity = models.BigIntegerField(
        verbose_name="수량",
    )

    total_price = models.BigIntegerField(
        verbose_name="총 금액",
    )

    memo = models.TextField(
        verbose_name="메모",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        verbose_name="생성일",
        auto_now_add=True,
    )
    modified_at = models.DateTimeField(
        verbose_name="마지막으로 수정된 날짜",
        auto_now=True,
    )


class InventoryHistory(models.Model):
    """재고 관리 이력
    """

    class Meta:
        verbose_name = "재고 관리 이력"
        verbose_name_plural = "재고 관리 이력"

    inventory = models.ForeignKey(
        Inventory,
        verbose_name="재고",
        on_delete=models.SET_NULL,
        null=True,
    )

    classification = models.CharField(
        verbose_name="구분",
        max_length=40,
        choices=(
            ("STORE", "입고"),
            ("RELEASE", "출고"),
        ),
        blank=True,
    )

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="관리자",
        on_delete=models.SET_NULL,
        null=True,
    )

    item = models.ForeignKey(
        Item,
        verbose_name="품목",
        on_delete=models.SET_NULL,
        null=True,
    )

    unit_price = models.BigIntegerField(
        verbose_name="단가",
    )

    quantity = models.BigIntegerField(
        verbose_name="수량",
    )

    total_price = models.BigIntegerField(
        verbose_name="총 금액",
    )

    memo = models.TextField(
        verbose_name="메모",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        verbose_name="생성일",
        auto_now_add=True,
    )
