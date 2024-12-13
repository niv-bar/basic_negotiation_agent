import math
from typing import Dict, Any, Optional


class NegotiationAgent:
    """
    Represents an agent participating in a negotiation, either as a customer or a wedding planner.

    Attributes:
        role (str): Role of the agent ('customer' or 'wedding_planner').
        preferences (Dict[str, Any]): Agent-specific preferences including budget, services, and timeline.
        budget_sensitivity (float): Sensitivity factor for budget utility calculations.
        utility_weights (Dict[str, Dict[str, float]]): Weights for budget, services, and timeline utilities.
    """

    def __init__(self, role: str, initial_preferences: Dict[str, Any]):
        """
        Initialize the negotiation agent with its role and preferences.

        Args:
            role (str): Role of the agent ('customer' or 'wedding_planner').
            initial_preferences (Dict[str, Any]): Initial preferences including budget, services, and timeline.
        """
        self.role = role
        self.preferences = initial_preferences

        # Sensitivity factors and utility weights
        self.budget_sensitivity = 5000
        self.utility_weights = {
            'customer': {
                'budget': 0.5,
                'services': 0.3,
                'timeline': 0.2
            },
            'wedding_planner': {
                'budget': 0.6,
                'services': 0.3,
                'timeline': 0.1
            }
        }

    def calculate_budget_utility(self, negotiated_budget: float) -> float:
        """
        Calculate budget utility based on the agent's role and preferences.

        Args:
            negotiated_budget (float): The budget being negotiated.

        Returns:
            float: The utility value for the negotiated budget.
        """
        if self.role == 'customer':
            # Logistic function for customer budget utility
            return 1 / (1 + math.exp((negotiated_budget - self.preferences['min_budget'])
                                     / self.budget_sensitivity))
        else:  # wedding_planner
            # Logarithmic function for planner budget utility
            return math.log(negotiated_budget / self.preferences['min_budget'])

    def calculate_services_utility(self, service_level: str) -> float:
        """
        Calculate utility for the provided service level.

        Args:
            service_level (str): The level of services ('Premium', 'Standard', 'Basic').

        Returns:
            float: The utility value for the service level.
        """
        service_utilities = {
            'customer': {
                'Premium': 1.0,
                'Standard': 0.7,
                'Basic': 0.4
            },
            'wedding_planner': {
                'Premium': 1.0,
                'Standard': 0.8,
                'Basic': 0.5
            }
        }
        return service_utilities[self.role][service_level]

    def calculate_timeline_utility(self, negotiated_timeline: float) -> float:
        """
        Calculate utility for the negotiated timeline.

        Args:
            negotiated_timeline (float): The timeline being negotiated.

        Returns:
            float: The utility value for the timeline.
        """
        if self.role == 'customer':
            return 1 - abs((negotiated_timeline - self.preferences['preferred_timeline'])
                           / self.preferences['max_timeline'])
        else:  # wedding_planner
            return 1 - (negotiated_timeline / self.preferences['max_timeline'])

    def calculate_total_utility(self, offer: Dict[str, Any]) -> float:
        """
        Calculate the total utility for a given offer using a weighted sum of utilities.

        Args:
            offer (Dict[str, Any]): The offer containing 'budget', 'services', and 'timeline'.

        Returns:
            float: The total utility value for the offer.
        """
        budget_utility = self.calculate_budget_utility(offer['budget'])
        services_utility = self.calculate_services_utility(offer['services'])
        timeline_utility = self.calculate_timeline_utility(offer['timeline'])

        weights = self.utility_weights[self.role]

        return (
                weights['budget'] * budget_utility +
                weights['services'] * services_utility +
                weights['timeline'] * timeline_utility
        )

    def generate_offer(self, previous_offer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an offer based on the agent's strategy.

        Args:
            previous_offer (Optional[Dict[str, Any]]): The previous offer made.

        Returns:
            Dict[str, Any]: The generated offer containing 'budget', 'services', and 'timeline'.
        """
        if previous_offer is None:
            return {
                'budget': self.preferences['optimal_budget'],
                'services': self.preferences['optimal_services'],
                'timeline': self.preferences['optimal_timeline']
            }

        if self.role == 'customer':
            return {
                'budget': min(previous_offer['budget'] * 1.05, self.preferences['max_budget']),
                'services': 'Standard' if previous_offer['services'] == 'Basic' else previous_offer['services'],
                'timeline': previous_offer['timeline']
            }
        else:  # wedding_planner
            return {
                'budget': previous_offer['budget'],
                'services': previous_offer['services'],
                'timeline': max(previous_offer['timeline'] * 0.9, self.preferences['min_timeline'])
            }

    def evaluate_offer(self, offer: Dict[str, Any]) -> bool:
        """
        Evaluate whether to accept an offer based on utility thresholds.

        Args:
            offer (Dict[str, Any]): The offer to evaluate.

        Returns:
            bool: True if the offer is acceptable, False otherwise.
        """
        utility = self.calculate_total_utility(offer)

        return utility >= (0.8 if self.role == 'customer' else 0.6)


class NegotiationSimulation:
    """
    Simulates the negotiation process between a customer and a wedding planner.

    Attributes:
        customer (NegotiationAgent): The customer agent.
        wedding_planner (NegotiationAgent): The wedding planner agent.
        max_rounds (int): Maximum number of negotiation rounds.
        current_round (int): Current round of the negotiation.
        negotiation_history (list): Log of all negotiation rounds.
    """

    def __init__(self, customer: NegotiationAgent, wedding_planner: NegotiationAgent):
        """
        Initialize the negotiation simulation.

        Args:
            customer (NegotiationAgent): The customer agent.
            wedding_planner (NegotiationAgent): The wedding planner agent.
        """
        self.customer = customer
        self.wedding_planner = wedding_planner
        self.max_rounds = 10
        self.current_round = 0
        self.negotiation_history = []

    def run_negotiation(self):
        """
        Simulate the negotiation process between the customer and the wedding planner.

        Returns:
            Optional[Dict[str, Any]]: The final agreed offer, or None if no agreement was reached.
        """
        customer_offer = self.customer.generate_offer()
        planner_offer = self.wedding_planner.generate_offer()

        print("Initial Offers:")
        print(f"Customer Offer: {customer_offer}")
        print(f"Wedding Planner Offer: {planner_offer}")

        current_offer = customer_offer
        current_agent = self.wedding_planner
        responding_agent = self.customer

        while self.current_round < self.max_rounds:
            self.current_round += 1
            print(f"\n--- Round {self.current_round} ---")

            is_accepted = responding_agent.evaluate_offer(current_offer)

            negotiation_round_info = {
                'round': self.current_round,
                'offering_agent': current_agent.role,
                'offer': current_offer,
                'accepted': is_accepted
            }
            self.negotiation_history.append(negotiation_round_info)

            print(f"{current_agent.role}'s Offer Evaluation:")
            print(f"Offer: {current_offer}")
            print(f"Accepted: {is_accepted}")

            if is_accepted:
                print("\n--- Agreement Reached! ---")
                print(f"Final Offer: {current_offer}")
                print(f"Total Rounds: {self.current_round}")
                return current_offer

            current_offer = current_agent.generate_offer(current_offer)
            current_agent, responding_agent = responding_agent, current_agent

        print("\n--- Negotiation Failed: Max Rounds Reached ---")
        return None


def main():
    """Run the negotiation simulation."""
    customer_preferences = {
        'min_budget': 10000,
        'max_budget': 50000,
        'optimal_budget': 15000,
        'optimal_services': 'Standard',
        'preferred_timeline': 6,
        'max_timeline': 12,
        'min_timeline': 3,
        'optimal_timeline': 6
    }

    planner_preferences = {
        'min_budget': 10000,
        'max_budget': 50000,
        'optimal_budget': 40000,
        'optimal_services': 'Premium',
        'preferred_timeline': 4,
        'max_timeline': 12,
        'min_timeline': 3,
        'optimal_timeline': 4
    }

    customer = NegotiationAgent('customer', customer_preferences)
    wedding_planner = NegotiationAgent('wedding_planner', planner_preferences)

    simulation = NegotiationSimulation(customer, wedding_planner)
    final_agreement = simulation.run_negotiation()

    print("\n--- Negotiation History ---")
    for round_info in simulation.negotiation_history:
        print(f"Round {round_info['round']}: {round_info['offering_agent']} offered {round_info['offer']}")


if __name__ == "__main__":
    main()
