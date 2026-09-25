"""Structural checks for proposal-only pin and peripheral assignments."""

from __future__ import annotations

from collections import defaultdict

from .models import EmbeddedDesign, EmbeddedValidationResult, PROPOSAL_ONLY


class EmbeddedValidator:
    def validate(self, design: EmbeddedDesign) -> EmbeddedValidationResult:
        issues: list[str] = []
        seen: set[str] = set()

        def add(code: str) -> None:
            if code not in seen:
                seen.add(code)
                issues.append(code)

        uses: list[tuple[str, str]] = []
        pins = set(design.mcu.pins)
        supported = set(design.mcu.supported_interfaces)

        def claim(pin: str, interface: str) -> None:
            if not pin:
                add("invalid configurations")
                return
            if interface not in supported:
                add("unsupported interfaces")
            if pin not in pins:
                add("invalid peripheral assignments")
            uses.append((pin, interface))

        for gpio in design.gpio:
            claim(gpio.pin, "GPIO")
            if gpio.direction not in {"input", "output"}:
                add("invalid configurations")
        for adc in design.adc:
            claim(adc.pin, "ADC")
            if not 1 <= adc.resolution_bits <= 24:
                add("invalid configurations")
        for pwm in design.pwm:
            claim(pwm.pin, "PWM")
            if pwm.frequency_hz <= 0 or not 0 <= pwm.duty_cycle <= 1:
                add("invalid configurations")
        for uart in design.uart:
            claim(uart.tx_pin, "UART")
            claim(uart.rx_pin, "UART")
            if uart.tx_pin == uart.rx_pin or uart.baud <= 0:
                add("invalid configurations")
        for spi in design.spi:
            spi_pins = [spi.sclk, spi.mosi, spi.miso, spi.cs]
            for pin in spi_pins:
                claim(pin, "SPI")
            if len(set(spi_pins)) != 4:
                add("invalid configurations")
        for bus in design.i2c:
            claim(bus.sda, "I2C")
            claim(bus.scl, "I2C")
            if bus.sda == bus.scl or not 1 <= bus.address <= 127:
                add("invalid configurations")
        timer_names: list[str] = []
        for timer in design.timers:
            timer_names.append(timer.name)
            if timer.pin:
                claim(timer.pin, "TIMER")
            if timer.period_ms <= 0 or not timer.name:
                add("invalid configurations")
        if len(timer_names) != len(set(timer_names)):
            add("resource conflicts")

        grouped: dict[str, list[str]] = defaultdict(list)
        for pin, interface in uses:
            grouped[pin].append(interface)
        for interfaces in grouped.values():
            if len(interfaces) < 2:
                continue
            if len(set(interfaces)) == 1:
                add("duplicate pins")
            else:
                add("pin conflicts")

        counts = {
            "GPIO": len(design.gpio),
            "ADC": len(design.adc),
            "PWM": len(design.pwm),
            "UART": len(design.uart),
            "SPI": len(design.spi),
            "I2C": len(design.i2c),
            "TIMER": len(design.timers),
        }
        for name, count in counts.items():
            limit = design.mcu.resources.get(name)
            if limit is not None and count > limit:
                add("resource conflicts")
        addresses = [bus.address for bus in design.i2c]
        if len(addresses) != len(set(addresses)):
            add("resource conflicts")

        return EmbeddedValidationResult(valid=not issues, issues=issues, mode=PROPOSAL_ONLY)
