import json
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class GroceryDeal:
    name: str
    price: float
    merchant: str

class MealPlanOptimizer:
    """
    Optimizes a selection of grocery deals to hit a specific budget target.
    Uses a dynamic programming subset-sum approach to find the exact combination
    that sums as closely to the user's budget as possible.
    """
    
    def __init__(self, tolerance: float = 2.0):
        self.tolerance = tolerance
        
    def find_optimal_plan(self, budget: float, available_deals: List[GroceryDeal]) -> Tuple[List[GroceryDeal], float]:
        """
        Finds the combination of deals that totals closest to the target budget.
        
        Args:
            budget: Target budget in dollars.
            available_deals: List of available grocery deals with extracted prices.
            
        Returns:
            Tuple containing:
            - List of selected GroceryDeal objects
            - Total price of the selected deals
        """
        if not available_deals:
            return [], 0.0
            
        # Shuffle deals so different meals are proposed each time
        random.shuffle(available_deals)
        
        # Optimization: prevent exponential explosion by limiting max items if too many
        if len(available_deals) > 40:
            # Take a random varied sample
            available_deals = available_deals[:40]
            
        target_cents = int(budget * 100)
        tolerance_cents = int(self.tolerance * 100)
        max_allowed_cents = target_cents + tolerance_cents
        
        # Maps an achievable sum (in cents) to the list of items that produce it
        achievable: Dict[int, List[GroceryDeal]] = {0: []}
        
        for item in available_deals:
            price_cents = int(item.price * 100)
            
            # We skip free items or items mathematically broken
            if price_cents <= 0:
                continue
                
            new_achievable = {}
            for current_sum, current_items in achievable.items():
                new_sum = current_sum + price_cents
                
                # We only track combinations that stay under our max tolerable budget
                if new_sum <= max_allowed_cents:
                    # Keep the first combination we find for this exact sum
                    if new_sum not in achievable and new_sum not in new_achievable:
                        new_achievable[new_sum] = current_items + [item]
                        
            achievable.update(new_achievable)
            
        # Find the sum closest to our target
        best_sum = 0
        smallest_diff = float('inf')
        
        for current_sum in achievable.keys():
            diff = abs(current_sum - target_cents)
            if diff < smallest_diff:
                smallest_diff = diff
                best_sum = current_sum
                
        # Are we within tolerance? The algorithm says it's ok to return the closest one
        # regardless, but ideally it hit within tolerance.
        selected_items = achievable[best_sum]
        total_price = best_sum / 100.0
        
        return selected_items, total_price


if __name__ == "__main__":
    print("--- Testing Meal Plan Budget Optimizer ---")
    
    mock_deals = [
        GroceryDeal("Chicken Breast", 12.99, "IGA"),
        GroceryDeal("Rice", 4.99, "Maxi"),
        GroceryDeal("Broccoli", 2.49, "Super C"),
        GroceryDeal("Apples", 3.99, "Walmart"),
        GroceryDeal("Milk", 5.49, "IGA"),
        GroceryDeal("Eggs", 3.49, "Maxi"),
        GroceryDeal("Bread", 2.99, "Super C"),
        GroceryDeal("Beef Ground", 8.99, "Walmart"),
        GroceryDeal("Pasta", 1.99, "IGA"),
        GroceryDeal("Tomato Sauce", 2.49, "Maxi")
    ]
    
    optimizer = MealPlanOptimizer(tolerance=2.0)
    
    budgets_to_test = [15.00, 25.00, 30.00]
    
    for budget in budgets_to_test:
        print(f"\nTarget Budget: ${budget:.2f} (Tolerance: ±${optimizer.tolerance:.2f})")
        selected, total = optimizer.find_optimal_plan(budget, mock_deals)
        
        print(f"Optimal Total Reached: ${total:.2f}")
        print("Selected Items:")
        for item in selected:
            print(f" - {item.name}: ${item.price:.2f} ({item.merchant})")
        
        diff = abs(total - budget)
        if diff <= optimizer.tolerance:
            print("✅ Successfully met tolerance requirement!")
        else:
            print(f"⚠️ Closest possible match found, off by ${diff:.2f}")
