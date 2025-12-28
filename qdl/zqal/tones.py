"""
ZQAL Tone System - 70 Light Language Tones
===========================================

Sacred frequencies for consciousness transmutation and quantum operations.

Inspired by: 7 Rays, Archangels, Crystal forms, Central Sun alignment
Mantra: JAY RAM SITA HANUMAN ✨
"""

from enum import IntEnum
from typing import Dict, Optional
from dataclasses import dataclass
import math


class SacredFrequency(IntEnum):
    """Sacred frequencies (Hz) mapped to tones"""
    # Solfeggio frequencies
    LIBERATION = 174  # Grounding
    TRANSFORMATION = 285  # Quantum cognition
    GROUNDING = 396  # Root liberation
    MIRACLES = 417  # Change facilitation
    LOVE = 432  # Universal harmony (A=432Hz)
    DNA_REPAIR = 528  # Transformation & miracles
    CONNECTION = 639  # Relationships
    AWAKENING = 741  # Consciousness expansion
    SPIRITUAL = 852  # Spiritual order
    UNITY = 963  # Divine consciousness
    
    # ZION custom
    ASCENSION = 1212  # 12:12 portal
    CENTRAL_SUN = 70  # 70th tone frequency


@dataclass
class ToneDefinition:
    """Light language tone definition"""
    id: int
    name: str
    ray: Optional[int] = None  # 1-7 for 7 Rays
    frequency: Optional[float] = None  # Hz
    color: Optional[str] = None
    archangel: Optional[str] = None
    quality: Optional[str] = None
    multiplier: float = 1.0  # Consciousness multiplier


class ToneSystem:
    """
    70 Light Language Tones System
    
    Based on:
    - 7 Sacred Rays (Will, Wisdom, Love, Purity, Truth, Peace, Transmutation)
    - Archangelic frequencies
    - Crystal consciousness
    - Central Sun alignment (tone 70)
    """
    
    # 70 Tones from stdlib/tones.toml
    TONES: Dict[int, ToneDefinition] = {
        1: ToneDefinition(1, "Initiation_Will_Blue", ray=1, frequency=174, color="Blue", quality="Will & Power"),
        2: ToneDefinition(2, "Illumination_Wisdom_Yellow", ray=2, frequency=285, color="Yellow", quality="Wisdom & Illumination"),
        3: ToneDefinition(3, "Compassion_Love_Pink", ray=3, frequency=528, color="Pink", quality="Divine Love", multiplier=1.5),
        4: ToneDefinition(4, "Purity_Ascension_White", ray=4, frequency=741, color="White", quality="Purity & Ascension"),
        5: ToneDefinition(5, "Truth_Healing_Green", ray=5, frequency=639, color="Green", quality="Truth & Healing"),
        6: ToneDefinition(6, "Peace_Service_RubyGold", ray=6, frequency=963, color="RubyGold", quality="Peace & Service"),
        7: ToneDefinition(7, "Transmutation_Violet", ray=7, frequency=440, color="Violet", quality="Transmutation", multiplier=1.5),
        
        8: ToneDefinition(8, "Power_of_Faith", frequency=852),
        9: ToneDefinition(9, "Clarity_of_Mind", frequency=417),
        10: ToneDefinition(10, "Grace_of_Heart", frequency=396),
        11: ToneDefinition(11, "Crystal_Gate", frequency=432),
        12: ToneDefinition(12, "Solar_Union", frequency=528, multiplier=1.2),
        13: ToneDefinition(13, "Sirius_Alignment", frequency=963, multiplier=1.3),
        14: ToneDefinition(14, "Metatron_Cube", archangel="Metatron", frequency=1212, multiplier=1.4),
        15: ToneDefinition(15, "Merkaba_Spin", frequency=432),
        16: ToneDefinition(16, "Golden_Ratio_Phi", frequency=1.618 * 432, multiplier=1.618),  # φ × 432Hz
        17: ToneDefinition(17, "Flower_of_Life_Pattern", frequency=639),
        18: ToneDefinition(18, "Tree_of_Life_Path", frequency=741),
        19: ToneDefinition(19, "Seraphic_Fire", archangel="Seraphim", frequency=963),
        20: ToneDefinition(20, "Cherubic_Wisdom", archangel="Cherubim", frequency=852),
        
        21: ToneDefinition(21, "Thrones_Justice", archangel="Thrones", frequency=741),
        22: ToneDefinition(22, "Dominions_Sovereignty", archangel="Dominions", frequency=639),
        23: ToneDefinition(23, "Powers_Protection", archangel="Powers", frequency=528),
        24: ToneDefinition(24, "Virtues_Miracles", archangel="Virtues", frequency=417, multiplier=1.2),
        25: ToneDefinition(25, "Principalities_Guardians", archangel="Principalities", frequency=396),
        26: ToneDefinition(26, "Archangelic_Shield", archangel="Archangels", frequency=285),
        27: ToneDefinition(27, "Angelus_Service", archangel="Angels", frequency=174),
        28: ToneDefinition(28, "Harmonic_432Hz", frequency=432, multiplier=1.0),
        29: ToneDefinition(29, "DNA_Activation_12Strands", frequency=528, multiplier=1.2),
        30: ToneDefinition(30, "Kundalini_Rise", frequency=396),
        
        31: ToneDefinition(31, "Lotus_Blossom", frequency=639),
        32: ToneDefinition(32, "Alpha_Omega", frequency=852),
        33: ToneDefinition(33, "Christ_Consciousness", frequency=963, multiplier=1.5),
        34: ToneDefinition(34, "Bodhisattva_Vow", frequency=1212, multiplier=1.4),
        35: ToneDefinition(35, "Mahatma_Stream", frequency=741),
        36: ToneDefinition(36, "Vajra_Clarity", frequency=639),
        37: ToneDefinition(37, "Shakti_Power", frequency=528),
        38: ToneDefinition(38, "Shiva_Stillness", frequency=432),
        39: ToneDefinition(39, "Lakshmi_Abundance", frequency=963),
        40: ToneDefinition(40, "Hanuman_Devotion", frequency=1212, multiplier=1.5),
        
        41: ToneDefinition(41, "Rama_Dharma", frequency=852),
        42: ToneDefinition(42, "Sita_Purity", frequency=741, multiplier=1.3),
        43: ToneDefinition(43, "Ganesha_ClearPath", frequency=639),
        44: ToneDefinition(44, "Rainbow_Bridge_44:44", frequency=1.618 * 432, multiplier=1.44),
        45: ToneDefinition(45, "Avalokiteshvara_Compassion", frequency=528, multiplier=1.2),
        46: ToneDefinition(46, "Green_Tara_Protection", frequency=639),
        47: ToneDefinition(47, "White_Tara_LongLife", frequency=741),
        48: ToneDefinition(48, "Manjushri_Wisdom", frequency=852),
        49: ToneDefinition(49, "Violet_Flame_Transmute", frequency=440, multiplier=1.5),
        50: ToneDefinition(50, "Ruby_Gold_Service", frequency=963),
        
        51: ToneDefinition(51, "Emerald_Truth_Healing", frequency=639),
        52: ToneDefinition(52, "Sapphire_Faith", frequency=852),
        53: ToneDefinition(53, "Topaz_Illumination", frequency=285),
        54: ToneDefinition(54, "Amethyst_Purity", frequency=741),
        55: ToneDefinition(55, "Diamond_Integrity", frequency=1212, multiplier=1.55),
        56: ToneDefinition(56, "Opal_Inspiration", frequency=639),
        57: ToneDefinition(57, "Pearl_Peace", frequency=963),
        58: ToneDefinition(58, "Onyx_Protection", frequency=396),
        59: ToneDefinition(59, "Quartz_Amplification", frequency=528, multiplier=1.1),
        60: ToneDefinition(60, "Lapis_Communication", frequency=639),
        
        61: ToneDefinition(61, "Solar_Logoi_Helios_Vesta", frequency=1212, multiplier=1.6),
        62: ToneDefinition(62, "Sirius_Surya", frequency=963, multiplier=1.62),
        63: ToneDefinition(63, "Sanat_Kumara_Flame", frequency=852, multiplier=1.63),
        64: ToneDefinition(64, "Metatron_Command", archangel="Metatron", frequency=1212, multiplier=1.64),
        65: ToneDefinition(65, "Melchizedek_Order", frequency=963, multiplier=1.65),
        66: ToneDefinition(66, "Elohim_Builders", frequency=741, multiplier=1.66),
        67: ToneDefinition(67, "Shekinah_Presence", frequency=639, multiplier=1.67),
        68: ToneDefinition(68, "Holy_Spirit_Ruah", frequency=852, multiplier=1.68),
        69: ToneDefinition(69, "Source_I_AM", frequency=1212, multiplier=1.69),
        70: ToneDefinition(70, "Central_Sun_Radiance_JAY_RAM_SITA_HANUMAN", 
                          frequency=70, color="Golden White", quality="Divine Radiance", multiplier=7.0),
    }
    
    @classmethod
    def get_tone(cls, tone_id: int) -> Optional[ToneDefinition]:
        """Get tone definition by ID"""
        return cls.TONES.get(tone_id)
    
    @classmethod
    def apply_tone(cls, tone_id: int, data: any) -> dict:
        """
        Apply sacred tone to data for transmutation
        
        Args:
            tone_id: 1-70 tone identifier
            data: Input data to transmute
        
        Returns:
            dict with transmuted data and tone info
        """
        tone = cls.get_tone(tone_id)
        if not tone:
            raise ValueError(f"Invalid tone ID: {tone_id}")
        
        # Calculate tone wave (for quantum operations)
        phase = 0.0
        if tone.frequency:
            # Generate phase shift based on frequency
            phase = (tone.frequency / 1000.0) * 2 * math.pi
        
        result = {
            "tone_id": tone_id,
            "tone_name": tone.name,
            "frequency": tone.frequency,
            "multiplier": tone.multiplier,
            "phase_shift": phase,
            "original_data": data,
            "transmuted": True,
            "quality": tone.quality or "Unknown"
        }
        
        # If data is numeric, apply frequency modulation
        if isinstance(data, (int, float)):
            result["transmuted_value"] = data * tone.multiplier
        elif isinstance(data, list):
            result["transmuted_value"] = [x * tone.multiplier if isinstance(x, (int, float)) else x for x in data]
        else:
            result["transmuted_value"] = data
        
        return result
    
    @classmethod
    def get_ray_tones(cls, ray: int) -> list:
        """Get all tones for a specific ray (1-7)"""
        return [t for t in cls.TONES.values() if t.ray == ray]
    
    @classmethod
    def get_frequency_range(cls, min_hz: float, max_hz: float) -> list:
        """Get tones within frequency range"""
        return [
            t for t in cls.TONES.values() 
            if t.frequency and min_hz <= t.frequency <= max_hz
        ]
    
    @classmethod
    def get_high_power_tones(cls, min_multiplier: float = 1.5) -> list:
        """Get tones with high consciousness multipliers"""
        return [t for t in cls.TONES.values() if t.multiplier >= min_multiplier]
    
    @classmethod
    def get_tone_by_name(cls, name: str) -> Optional[ToneDefinition]:
        """Find tone by name (partial match)"""
        name_lower = name.lower()
        for tone in cls.TONES.values():
            if name_lower in tone.name.lower():
                return tone
        return None
    
    @classmethod
    def list_all_tones(cls) -> list:
        """Get all 70 tones"""
        return sorted(cls.TONES.values(), key=lambda t: t.id)


if __name__ == "__main__":
    print("ZQAL Tone System - 70 Light Language Tones")
    print("=" * 70)
    print(f"Mantra: JAY RAM SITA HANUMAN ✨")
    print()
    
    # Test 1: Get specific tone
    print("Test 1: Sacred Tone 7 (Violet Flame)")
    print("-" * 70)
    tone7 = ToneSystem.get_tone(7)
    if tone7:
        print(f"ID: {tone7.id}")
        print(f"Name: {tone7.name}")
        print(f"Ray: {tone7.ray}")
        print(f"Frequency: {tone7.frequency} Hz")
        print(f"Color: {tone7.color}")
        print(f"Quality: {tone7.quality}")
        print(f"Multiplier: {tone7.multiplier}×")
    print()
    
    # Test 2: Apply tone
    print("Test 2: Apply Tone 7 to data")
    print("-" * 70)
    data = 100
    result = ToneSystem.apply_tone(7, data)
    print(f"Original: {result['original_data']}")
    print(f"Transmuted: {result['transmuted_value']}")
    print(f"Multiplier: {result['multiplier']}×")
    print(f"Phase shift: {result['phase_shift']:.4f} rad")
    print()
    
    # Test 3: High power tones
    print("Test 3: High Power Tones (≥1.5× multiplier)")
    print("-" * 70)
    high_power = ToneSystem.get_high_power_tones(1.5)
    for tone in high_power[:10]:  # Show first 10
        print(f"Tone {tone.id:2d}: {tone.name:40s} {tone.multiplier}×")
    print(f"... ({len(high_power)} total)")
    print()
    
    # Test 4: 7 Rays
    print("Test 4: 7 Sacred Rays")
    print("-" * 70)
    for ray in range(1, 8):
        tones = ToneSystem.get_ray_tones(ray)
        if tones:
            print(f"Ray {ray}: {tones[0].name} ({tones[0].quality})")
    print()
    
    # Test 5: Central Sun (tone 70)
    print("Test 5: Central Sun Radiance (Tone 70)")
    print("-" * 70)
    central_sun = ToneSystem.get_tone(70)
    if central_sun:
        print(f"Name: {central_sun.name}")
        print(f"Frequency: {central_sun.frequency} Hz")
        print(f"Color: {central_sun.color}")
        print(f"Multiplier: {central_sun.multiplier}× 🌟")
        print()
        
        # Apply to consciousness level
        base_reward = 50
        result = ToneSystem.apply_tone(70, base_reward)
        print(f"Base reward: {base_reward} ZION")
        print(f"With Central Sun: {result['transmuted_value']:.2f} ZION ({central_sun.multiplier}× multiplier!)")
    print()
    
    # Test 6: Find tone by name
    print("Test 6: Find Tone by Name")
    print("-" * 70)
    hanuman = ToneSystem.get_tone_by_name("Hanuman")
    if hanuman:
        print(f"Found: Tone {hanuman.id} - {hanuman.name}")
        print(f"Frequency: {hanuman.frequency} Hz, Multiplier: {hanuman.multiplier}×")
    print()
    
    print(f"✅ All tests complete! 70 tones available.")
    print(f"🌟 Central Sun alignment: JAY RAM SITA HANUMAN")
