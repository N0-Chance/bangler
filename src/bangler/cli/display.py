import sys
from typing import Union
from ..models.bangle import BangleSpec
from ..models.pricing import BanglePrice, PricingError
from ..utils.formatting import BusinessFormatter

class CLIDisplay:
    """Terminal display formatting for CLI interface"""

    @staticmethod
    def show_welcome():
        """Display welcome message"""
        print("""
╔════════════════════════════════════════╗
║        Askew Jewelers Bangler          ║
║     Custom Bangle Pricing System       ║
╚════════════════════════════════════════╝

Real-time pricing based on current Stuller material costs.
""")

    @staticmethod
    def show_calculating():
        """Show calculation in progress"""
        print("\n🔄 Calculating pricing...")

    @staticmethod
    def show_progress_step(step: str, data: str = None):
        """Show individual progress step with optional data"""
        if data:
            print(f"   • {step}: {data}")
        else:
            print(f"   • {step}...")

    @staticmethod
    def show_price_result(result: Union[BanglePrice, PricingError]):
        """Display pricing result or error"""
        if isinstance(result, PricingError):
            CLIDisplay._show_error(result)
        else:
            CLIDisplay._show_success(result)

    @staticmethod
    def _show_success(price: BanglePrice):
        """Display successful pricing calculation"""
        breakdown = price.get_breakdown_display()

        print("\n✅ Pricing Calculation Complete!")
        print(BusinessFormatter.format_price_breakdown(breakdown))

        print(f"\n📋 Details:")
        print(f"   Stuller SKU: {price.sku}")
        print(f"   Material Cost per DWT: ${price.material_cost_per_dwt:.2f}")
        print(f"   Material Length Needed: {price.material_length_in:.2f} inches")

        # Highlight the final price
        print(f"\n💰 FINAL CUSTOMER PRICE: ${price.total_price:.2f}")
        print("=" * 50)

    @staticmethod
    def _show_error(error: PricingError):
        """Display error message with suggested action"""
        print(f"\n❌ {error.user_message}")
        print(f"\n💡 Suggested Action: {error.suggested_action}")

        if error.error_type == 'sku_not_found':
            print("\n🔍 Available alternatives:")
            print("   • Try a different width or thickness")
            print("   • Check with suppliers for special orders")
            print("   • Consider similar metal shapes")
        elif error.error_type == 'api_unavailable':
            print("\n🔄 Backup options:")
            print("   • Wait 5 minutes and try again")
            print("   • Use manual pricing methods")
            print("   • Contact technical support")

    @staticmethod
    def show_specification_summary(spec: BangleSpec):
        """Display customer specification summary"""
        print(f"\n📋 Customer Specification:")
        print(f"   Size: {spec.size}")
        print(f"   Metal: {spec.to_quality_string()}")
        print(f"   Shape: {spec.metal_shape}")
        print(f"   Dimensions: {spec.width} × {spec.thickness}")

    @staticmethod
    def prompt_continue() -> bool:
        """Ask if user wants to calculate another price"""
        response = input("\nWould you like to price another bangle? (y/n): ").lower().strip()
        return response in ['y', 'yes', '1', 'true']

    @staticmethod
    def show_goodbye():
        """Display goodbye message"""
        print("""
Thank you for using the Askew Jewelers Bangler!

For technical support or questions:
    support@askewjewelers.com

Have a great day! 💍 
""")