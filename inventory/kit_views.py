from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Kit, KitItem, Item, InventoryTransaction

@login_required
def kit_list(request):
    kits = Kit.objects.filter(is_active=True)
    return render(request, 'inventory/kit_list.html', {'kits': kits})

@login_required
def kit_assemble(request, pk):
    kit = get_object_or_404(Kit, pk=pk)
    
    if request.method == 'POST':
        quantity_to_assemble = int(request.POST.get('quantity', 0))
        
        if quantity_to_assemble <= 0:
            messages.error(request, "Please enter a valid quantity.")
            return redirect('inventory:kit_list')

        # Check if we have enough stock for all items in the kit
        can_assemble = True
        missing_items = []
        
        with transaction.atomic():
            for kit_item in kit.items.all():
                total_needed = kit_item.quantity * quantity_to_assemble
                if kit_item.item.stock_quantity < total_needed:
                    can_assemble = False
                    missing_items.append(f"{kit_item.item.name} (Need {total_needed}, have {kit_item.item.stock_quantity})")
            
            if not can_assemble:
                messages.error(request, f"Insufficient stock to assemble {quantity_to_assemble} kits: " + ", ".join(missing_items))
                return redirect('inventory:kit_list')

            # Deduct stock
            for kit_item in kit.items.all():
                needed = kit_item.quantity * quantity_to_assemble
                kit_item.item.stock_quantity -= needed
                kit_item.item.save()
                
                # Log transaction
                InventoryTransaction.objects.create(
                    item=kit_item.item,
                    transaction_type='DEDUCT',
                    quantity=needed,
                    reason=f"Assembled {quantity_to_assemble} units of {kit.name}",
                    performed_by=request.user
                )

            # Find or create the "Kit" item to store the assembled stock
            kit_stock_item, created = Item.objects.get_or_create(
                name=kit.name,
                defaults={'category': 'Assembled Kits', 'unit': 'KIT', 'description': kit.description}
            )
            kit_stock_item.stock_quantity += quantity_to_assemble
            kit_stock_item.save()

            messages.success(request, f"Successfully assembled {quantity_to_assemble} units of {kit.name}.")
            
    return redirect('inventory:kit_list')

@login_required
def kit_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        kit = Kit.objects.create(name=name, description=description)
        return redirect('inventory:kit_edit', pk=kit.pk)
    return redirect('inventory:kit_list')

@login_required
def kit_edit(request, pk):
    kit = get_object_or_404(Kit, pk=pk)
    items = Item.objects.all()
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        item = get_object_or_404(Item, pk=item_id)
        KitItem.objects.update_or_create(
            kit=kit, item=item,
            defaults={'quantity': quantity}
        )
        messages.success(request, f"Added {item.name} to {kit.name}")
        return redirect('inventory:kit_edit', pk=kit.pk)
        
    return render(request, 'inventory/kit_edit.html', {
        'kit': kit,
        'items': items
    })

@login_required
def kit_remove_item(request, kit_pk, item_pk):
    kit_item = get_object_or_404(KitItem, kit_id=kit_pk, pk=item_pk)
    kit_item.delete()
    messages.warning(request, "Item removed from kit.")
    return redirect('inventory:kit_edit', pk=kit_pk)
