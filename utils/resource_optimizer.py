import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime

class ResourceOptimizer:
    def __init__(self):
        self.priority_weights = {
            'High': 3,
            'Medium': 2,
            'Low': 1
        }
        
    def calculate_resource_needs(self, population: int, severity: str, response_rate: float) -> Dict[str, int]:
        """Calculate optimal resource allocation based on population and severity"""
        # Base resource requirements per 100 people
        base_requirements = {
            'Emergency Vehicles': 2,
            'Medical Supplies (units)': 100,
            'Relief Camps': 1,
            'Food Supplies (kg)': 300,
            'Water (liters)': 500,
            'Emergency Personnel': 5
        }
        
        # Adjust for severity
        severity_multiplier = self.priority_weights[severity]
        
        # Adjust for response rate (lower response rate means more resources needed)
        response_multiplier = 1 + (1 - response_rate)
        
        # Calculate actual requirements
        population_factor = population / 100
        requirements = {}
        
        for resource, base_amount in base_requirements.items():
            adjusted_amount = int(base_amount * population_factor * severity_multiplier * response_multiplier)
            requirements[resource] = adjusted_amount
            
        return requirements
    
    def optimize_allocation(
        self,
        available_resources: Dict[str, int],
        alerts: Dict[str, Dict],
        evacuation_data: Dict[str, Dict]
    ) -> Dict[str, Dict[str, int]]:
        """Optimize resource allocation across multiple locations"""
        allocations = {}
        priority_score = {}
        
        # Calculate priority scores for each location
        for alert_id, alert_data in alerts.items():
            evac_data = evacuation_data.get(alert_id, {})
            if not evac_data:
                continue
                
            response_rate = (evac_data['confirmed'] / evac_data['total']) if evac_data['total'] > 0 else 1
            population = evac_data['total']
            severity = alert_data['severity']
            
            # Calculate priority score based on multiple factors
            priority_score[alert_id] = (
                self.priority_weights[severity] *
                population *
                (1 - response_rate)  # Lower response rate = higher priority
            )
        
        # Sort locations by priority
        sorted_locations = sorted(
            priority_score.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Allocate resources based on priority
        remaining_resources = available_resources.copy()
        
        for alert_id, _ in sorted_locations:
            evac_data = evacuation_data[alert_id]
            alert_data = alerts[alert_id]
            
            # Calculate optimal resource needs
            needed_resources = self.calculate_resource_needs(
                population=evac_data['total'],
                severity=alert_data['severity'],
                response_rate=evac_data['confirmed'] / evac_data['total']
            )
            
            # Allocate available resources
            allocation = {}
            for resource, needed in needed_resources.items():
                available = remaining_resources.get(resource, 0)
                allocated = min(needed, available)
                allocation[resource] = allocated
                remaining_resources[resource] = available - allocated
            
            allocations[alert_id] = allocation
        
        return allocations

    def calculate_efficiency_metrics(
        self,
        allocations: Dict[str, Dict[str, int]],
        total_resources: Dict[str, int]
    ) -> Dict[str, float]:
        """Calculate resource allocation efficiency metrics"""
        metrics = {
            'resource_utilization': 0.0,
            'allocation_balance': 0.0,
            'coverage_ratio': 0.0
        }
        
        if not allocations or not total_resources:
            return metrics
            
        # Calculate resource utilization
        total_allocated = sum(sum(resources.values()) for resources in allocations.values())
        total_available = sum(total_resources.values())
        metrics['resource_utilization'] = total_allocated / total_available if total_available > 0 else 0
        
        # Calculate allocation balance (standard deviation of allocation ratios)
        allocation_ratios = []
        for location_allocation in allocations.values():
            for resource, amount in location_allocation.items():
                if total_resources.get(resource, 0) > 0:
                    ratio = amount / total_resources[resource]
                    allocation_ratios.append(ratio)
        
        if allocation_ratios:
            metrics['allocation_balance'] = 1 - np.std(allocation_ratios)
        
        # Calculate coverage ratio (locations served / total locations)
        metrics['coverage_ratio'] = len(allocations) / len(total_resources) if total_resources else 0
        
        return metrics
