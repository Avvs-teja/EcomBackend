from django.contrib import admin
from .models import Product, Customer, Orders, OrderItem

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'customer_name', 'email', 'phone_number', 'address', 'city', 'state','is_active','last_login')
    readonly_fields = ('username', 'customer_name', 'email', 'phone_number', 'address', 'city', 'state','is_active','last_login', 'profile_picture')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Do not display extra empty fields

class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'created_at', 'shipping_status')
    search_fields = ('user__username', 'id')  # Allow searching by user and order ID
    list_filter = ('created_at','shipping_status')  # Allow filtering by creation date
    inlines = [OrderItemInline]  # Display order items inline
    readonly_fields = ('id', 'user', 'total_amount', 'created_at')  # Ensure these fields are read-only

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('shipping_status',)
        else:  # Adding a new object
            return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion of orders in admin

admin.site.register(Product)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Orders, OrdersAdmin)
