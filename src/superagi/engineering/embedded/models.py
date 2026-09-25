"""Proposal-only embedded abstractions. Nothing here talks to a device."""

from __future__ import annotations

from pydantic import Field

from ..models import EM

PROPOSAL_ONLY = "PROPOSAL_ONLY"
_INTERFACES = ["GPIO", "ADC", "PWM", "UART", "SPI", "I2C", "TIMER"]


class MCU(EM):
    name: str
    pins: list[str]
    supported_interfaces: list[str] = Field(default_factory=lambda: list(_INTERFACES))
    resources: dict[str, int] = Field(default_factory=lambda: {"GPIO": 32, "ADC": 8, "PWM": 8, "UART": 2, "SPI": 1, "I2C": 1, "TIMER": 4})
    mode: str = PROPOSAL_ONLY


class GPIO(EM):
    pin: str
    direction: str
    mode: str = PROPOSAL_ONLY


class ADC(EM):
    pin: str
    resolution_bits: int = 12
    mode: str = PROPOSAL_ONLY


class PWM(EM):
    pin: str
    frequency_hz: float
    duty_cycle: float
    mode: str = PROPOSAL_ONLY


class UART(EM):
    tx_pin: str
    rx_pin: str
    baud: int = 115200
    mode: str = PROPOSAL_ONLY


class SPI(EM):
    sclk: str
    mosi: str
    miso: str
    cs: str
    mode: str = PROPOSAL_ONLY


class I2C(EM):
    sda: str
    scl: str
    address: int = 0x48
    mode: str = PROPOSAL_ONLY


class Timer(EM):
    name: str
    pin: str | None = None
    period_ms: float
    mode: str = PROPOSAL_ONLY


class EmbeddedDesign(EM):
    mcu: MCU
    gpio: list[GPIO] = Field(default_factory=list)
    adc: list[ADC] = Field(default_factory=list)
    pwm: list[PWM] = Field(default_factory=list)
    uart: list[UART] = Field(default_factory=list)
    spi: list[SPI] = Field(default_factory=list)
    i2c: list[I2C] = Field(default_factory=list)
    timers: list[Timer] = Field(default_factory=list)
    mode: str = PROPOSAL_ONLY


class EmbeddedValidationResult(EM):
    valid: bool
    issues: list[str] = Field(default_factory=list)
    mode: str = PROPOSAL_ONLY
