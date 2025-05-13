"""
Unit tests for IO system module
"""

import os
import pytest
import time
from unittest.mock import MagicMock, patch

from arkos.io.io_manager import IOManager
from arkos.io.gpio_controller import GPIOController
from arkos.io.relay_controller import RelayController


class TestIOManager:
    """Tests for the IOManager class"""

    def test_init(self):
        """Test initialization of IOManager"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [17, 18, 27],
                    "output": [22, 23, 24],
                },
                "relays": [
                    {
                        "name": "relay1",
                        "pin": 22,
                        "normally_open": True,
                    },
                    {
                        "name": "relay2",
                        "pin": 23,
                        "normally_open": False,
                    },
                ],
            }
        }
        
        with patch("arkos.io.io_manager.GPIOController") as mock_gpio_class, \
             patch("arkos.io.io_manager.RelayController") as mock_relay_class:
            
            # Mock GPIO and Relay controllers
            mock_gpio = MagicMock()
            mock_relay = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            mock_relay_class.return_value = mock_relay
            
            # Create IO manager
            manager = IOManager(config)
            
            # Check that controllers were created
            assert manager.enabled is True
            assert manager.gpio_controller == mock_gpio
            assert manager.relay_controller == mock_relay
            
            # Check that controllers were initialized with correct config
            mock_gpio_class.assert_called_once_with(config["io"]["gpio_pins"])
            mock_relay_class.assert_called_once_with(config["io"]["relays"])

    def test_disabled_manager(self):
        """Test IOManager when disabled"""
        config = {
            "io": {
                "enabled": False,
            }
        }
        
        with patch("arkos.io.io_manager.GPIOController") as mock_gpio_class, \
             patch("arkos.io.io_manager.RelayController") as mock_relay_class:
            
            # Create IO manager
            manager = IOManager(config)
            
            # Check that controllers were not created
            assert manager.enabled is False
            assert manager.gpio_controller is None
            assert manager.relay_controller is None
            
            # Check that controllers were not initialized
            mock_gpio_class.assert_not_called()
            mock_relay_class.assert_not_called()

    def test_setup(self):
        """Test setting up IO manager"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [17, 18, 27],
                    "output": [22, 23, 24],
                },
                "relays": [
                    {
                        "name": "relay1",
                        "pin": 22,
                        "normally_open": True,
                    },
                ],
            }
        }
        
        with patch("arkos.io.io_manager.GPIOController") as mock_gpio_class, \
             patch("arkos.io.io_manager.RelayController") as mock_relay_class:
            
            # Mock GPIO and Relay controllers
            mock_gpio = MagicMock()
            mock_relay = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            mock_relay_class.return_value = mock_relay
            
            # Create IO manager
            manager = IOManager(config)
            
            # Setup IO manager
            manager.setup()
            
            # Check that controllers were set up
            mock_gpio.setup.assert_called_once()
            mock_relay.setup.assert_called_once()

    def test_cleanup(self):
        """Test cleaning up IO manager"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [17, 18, 27],
                    "output": [22, 23, 24],
                },
                "relays": [
                    {
                        "name": "relay1",
                        "pin": 22,
                        "normally_open": True,
                    },
                ],
            }
        }
        
        with patch("arkos.io.io_manager.GPIOController") as mock_gpio_class, \
             patch("arkos.io.io_manager.RelayController") as mock_relay_class:
            
            # Mock GPIO and Relay controllers
            mock_gpio = MagicMock()
            mock_relay = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            mock_relay_class.return_value = mock_relay
            
            # Create IO manager
            manager = IOManager(config)
            
            # Cleanup IO manager
            manager.cleanup()
            
            # Check that controllers were cleaned up
            mock_gpio.cleanup.assert_called_once()
            mock_relay.cleanup.assert_called_once()

    def test_get_input_state(self):
        """Test getting input state"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [17, 18, 27],
                    "output": [22, 23, 24],
                },
                "relays": [],
            }
        }
        
        with patch("arkos.io.io_manager.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Mock get_input_state
            mock_gpio.get_input_state.return_value = True
            
            # Create IO manager
            manager = IOManager(config)
            
            # Get input state
            state = manager.get_input_state(17)
            
            # Check that GPIO controller was called
            mock_gpio.get_input_state.assert_called_once_with(17)
            
            # Check result
            assert state is True

    def test_set_output_state(self):
        """Test setting output state"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [17, 18, 27],
                    "output": [22, 23, 24],
                },
                "relays": [],
            }
        }
        
        with patch("arkos.io.io_manager.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Create IO manager
            manager = IOManager(config)
            
            # Set output state
            manager.set_output_state(22, True)
            
            # Check that GPIO controller was called
            mock_gpio.set_output_state.assert_called_once_with(22, True)

    def test_activate_relay(self):
        """Test activating a relay"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [],
                    "output": [22, 23],
                },
                "relays": [
                    {
                        "name": "relay1",
                        "pin": 22,
                        "normally_open": True,
                    },
                    {
                        "name": "relay2",
                        "pin": 23,
                        "normally_open": False,
                    },
                ],
            }
        }
        
        with patch("arkos.io.io_manager.RelayController") as mock_relay_class:
            # Mock Relay controller
            mock_relay = MagicMock()
            mock_relay_class.return_value = mock_relay
            
            # Create IO manager
            manager = IOManager(config)
            
            # Activate relay
            manager.activate_relay("relay1")
            
            # Check that Relay controller was called
            mock_relay.activate.assert_called_once_with("relay1")

    def test_deactivate_relay(self):
        """Test deactivating a relay"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [],
                    "output": [22, 23],
                },
                "relays": [
                    {
                        "name": "relay1",
                        "pin": 22,
                        "normally_open": True,
                    },
                    {
                        "name": "relay2",
                        "pin": 23,
                        "normally_open": False,
                    },
                ],
            }
        }
        
        with patch("arkos.io.io_manager.RelayController") as mock_relay_class:
            # Mock Relay controller
            mock_relay = MagicMock()
            mock_relay_class.return_value = mock_relay
            
            # Create IO manager
            manager = IOManager(config)
            
            # Deactivate relay
            manager.deactivate_relay("relay1")
            
            # Check that Relay controller was called
            mock_relay.deactivate.assert_called_once_with("relay1")

    def test_get_relay_state(self):
        """Test getting relay state"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [],
                    "output": [22, 23],
                },
                "relays": [
                    {
                        "name": "relay1",
                        "pin": 22,
                        "normally_open": True,
                    },
                ],
            }
        }
        
        with patch("arkos.io.io_manager.RelayController") as mock_relay_class:
            # Mock Relay controller
            mock_relay = MagicMock()
            mock_relay_class.return_value = mock_relay
            
            # Mock get_state
            mock_relay.get_state.return_value = True
            
            # Create IO manager
            manager = IOManager(config)
            
            # Get relay state
            state = manager.get_relay_state("relay1")
            
            # Check that Relay controller was called
            mock_relay.get_state.assert_called_once_with("relay1")
            
            # Check result
            assert state is True

    def test_pulse_relay(self):
        """Test pulsing a relay"""
        config = {
            "io": {
                "enabled": True,
                "gpio_pins": {
                    "input": [],
                    "output": [22],
                },
                "relays": [
                    {
                        "name": "relay1",
                        "pin": 22,
                        "normally_open": True,
                    },
                ],
            }
        }
        
        with patch("arkos.io.io_manager.RelayController") as mock_relay_class:
            # Mock Relay controller
            mock_relay = MagicMock()
            mock_relay_class.return_value = mock_relay
            
            # Create IO manager
            manager = IOManager(config)
            
            # Pulse relay
            manager.pulse_relay("relay1", 0.5)
            
            # Check that Relay controller was called
            mock_relay.pulse.assert_called_once_with("relay1", 0.5)


class TestGPIOController:
    """Tests for the GPIOController class"""

    @patch("arkos.io.gpio_controller.GPIO")
    def test_init(self, mock_gpio):
        """Test initialization of GPIOController"""
        config = {
            "input": [17, 18, 27],
            "output": [22, 23, 24],
        }
        
        controller = GPIOController(config)
        
        assert controller.input_pins == [17, 18, 27]
        assert controller.output_pins == [22, 23, 24]
        assert controller.gpio == mock_gpio

    @patch("arkos.io.gpio_controller.GPIO")
    def test_setup(self, mock_gpio):
        """Test setting up GPIO controller"""
        config = {
            "input": [17, 18],
            "output": [22, 23],
        }
        
        controller = GPIOController(config)
        
        # Setup controller
        controller.setup()
        
        # Check that GPIO was set up
        mock_gpio.setmode.assert_called_once_with(mock_gpio.BCM)
        
        # Check that input pins were set up
        assert mock_gpio.setup.call_count == 4  # 2 inputs + 2 outputs
        mock_gpio.setup.assert_any_call(17, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP)
        mock_gpio.setup.assert_any_call(18, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP)
        mock_gpio.setup.assert_any_call(22, mock_gpio.OUT, initial=mock_gpio.LOW)
        mock_gpio.setup.assert_any_call(23, mock_gpio.OUT, initial=mock_gpio.LOW)

    @patch("arkos.io.gpio_controller.GPIO")
    def test_cleanup(self, mock_gpio):
        """Test cleaning up GPIO controller"""
        config = {
            "input": [17, 18],
            "output": [22, 23],
        }
        
        controller = GPIOController(config)
        
        # Cleanup controller
        controller.cleanup()
        
        # Check that GPIO was cleaned up
        mock_gpio.cleanup.assert_called_once()

    @patch("arkos.io.gpio_controller.GPIO")
    def test_get_input_state(self, mock_gpio):
        """Test getting input state"""
        config = {
            "input": [17, 18],
            "output": [22, 23],
        }
        
        controller = GPIOController(config)
        
        # Mock input state
        mock_gpio.input.return_value = True
        
        # Get input state
        state = controller.get_input_state(17)
        
        # Check that GPIO was called
        mock_gpio.input.assert_called_once_with(17)
        
        # Check result
        assert state is True

    @patch("arkos.io.gpio_controller.GPIO")
    def test_set_output_state(self, mock_gpio):
        """Test setting output state"""
        config = {
            "input": [17, 18],
            "output": [22, 23],
        }
        
        controller = GPIOController(config)
        
        # Set output state
        controller.set_output_state(22, True)
        
        # Check that GPIO was called
        mock_gpio.output.assert_called_once_with(22, mock_gpio.HIGH)
        
        # Set output state to False
        controller.set_output_state(22, False)
        
        # Check that GPIO was called again
        mock_gpio.output.assert_called_with(22, mock_gpio.LOW)

    @patch("arkos.io.gpio_controller.GPIO")
    def test_add_event_callback(self, mock_gpio):
        """Test adding event callback"""
        config = {
            "input": [17, 18],
            "output": [22, 23],
        }
        
        controller = GPIOController(config)
        
        # Create callback function
        callback = MagicMock()
        
        # Add event callback
        controller.add_event_callback(17, callback, "RISING")
        
        # Check that GPIO was called
        mock_gpio.add_event_detect.assert_called_once_with(
            17, mock_gpio.RISING, callback=callback, bouncetime=200
        )

    @patch("arkos.io.gpio_controller.GPIO")
    def test_remove_event_callback(self, mock_gpio):
        """Test removing event callback"""
        config = {
            "input": [17, 18],
            "output": [22, 23],
        }
        
        controller = GPIOController(config)
        
        # Remove event callback
        controller.remove_event_callback(17)
        
        # Check that GPIO was called
        mock_gpio.remove_event_detect.assert_called_once_with(17)


class TestRelayController:
    """Tests for the RelayController class"""

    def test_init(self):
        """Test initialization of RelayController"""
        config = [
            {
                "name": "relay1",
                "pin": 22,
                "normally_open": True,
            },
            {
                "name": "relay2",
                "pin": 23,
                "normally_open": False,
            },
        ]
        
        with patch("arkos.io.relay_controller.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Create Relay controller
            controller = RelayController(config)
            
            # Check that relays were configured
            assert len(controller.relays) == 2
            assert controller.relays["relay1"]["pin"] == 22
            assert controller.relays["relay1"]["normally_open"] is True
            assert controller.relays["relay1"]["active"] is False
            assert controller.relays["relay2"]["pin"] == 23
            assert controller.relays["relay2"]["normally_open"] is False
            assert controller.relays["relay2"]["active"] is False
            
            # Check that GPIO controller was created
            assert controller.gpio == mock_gpio

    def test_setup(self):
        """Test setting up Relay controller"""
        config = [
            {
                "name": "relay1",
                "pin": 22,
                "normally_open": True,
            },
        ]
        
        with patch("arkos.io.relay_controller.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Create Relay controller
            controller = RelayController(config)
            
            # Setup controller
            controller.setup()
            
            # Check that GPIO controller was set up
            mock_gpio.setup.assert_called_once()

    def test_cleanup(self):
        """Test cleaning up Relay controller"""
        config = [
            {
                "name": "relay1",
                "pin": 22,
                "normally_open": True,
            },
        ]
        
        with patch("arkos.io.relay_controller.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Create Relay controller
            controller = RelayController(config)
            
            # Cleanup controller
            controller.cleanup()
            
            # Check that GPIO controller was cleaned up
            mock_gpio.cleanup.assert_called_once()

    def test_activate(self):
        """Test activating a relay"""
        config = [
            {
                "name": "relay1",
                "pin": 22,
                "normally_open": True,
            },
            {
                "name": "relay2",
                "pin": 23,
                "normally_open": False,
            },
        ]
        
        with patch("arkos.io.relay_controller.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Create Relay controller
            controller = RelayController(config)
            
            # Activate relays
            controller.activate("relay1")
            controller.activate("relay2")
            
            # Check that GPIO controller was called
            mock_gpio.set_output_state.assert_any_call(22, True)  # NO relay: HIGH to activate
            mock_gpio.set_output_state.assert_any_call(23, False)  # NC relay: LOW to activate
            
            # Check relay state
            assert controller.relays["relay1"]["active"] is True
            assert controller.relays["relay2"]["active"] is True

    def test_deactivate(self):
        """Test deactivating a relay"""
        config = [
            {
                "name": "relay1",
                "pin": 22,
                "normally_open": True,
            },
            {
                "name": "relay2",
                "pin": 23,
                "normally_open": False,
            },
        ]
        
        with patch("arkos.io.relay_controller.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Create Relay controller
            controller = RelayController(config)
            
            # Set relays as active
            controller.relays["relay1"]["active"] = True
            controller.relays["relay2"]["active"] = True
            
            # Deactivate relays
            controller.deactivate("relay1")
            controller.deactivate("relay2")
            
            # Check that GPIO controller was called
            mock_gpio.set_output_state.assert_any_call(22, False)  # NO relay: LOW to deactivate
            mock_gpio.set_output_state.assert_any_call(23, True)  # NC relay: HIGH to deactivate
            
            # Check relay state
            assert controller.relays["relay1"]["active"] is False
            assert controller.relays["relay2"]["active"] is False

    def test_get_state(self):
        """Test getting relay state"""
        config = [
            {
                "name": "relay1",
                "pin": 22,
                "normally_open": True,
            },
        ]
        
        with patch("arkos.io.relay_controller.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Create Relay controller
            controller = RelayController(config)
            
            # Set relay as active
            controller.relays["relay1"]["active"] = True
            
            # Get relay state
            state = controller.get_state("relay1")
            
            # Check result
            assert state is True
            
            # Set relay as inactive
            controller.relays["relay1"]["active"] = False
            
            # Get relay state
            state = controller.get_state("relay1")
            
            # Check result
            assert state is False

    @patch("arkos.io.relay_controller.time.sleep")
    def test_pulse(self, mock_sleep):
        """Test pulsing a relay"""
        config = [
            {
                "name": "relay1",
                "pin": 22,
                "normally_open": True,
            },
        ]
        
        with patch("arkos.io.relay_controller.GPIOController") as mock_gpio_class:
            # Mock GPIO controller
            mock_gpio = MagicMock()
            mock_gpio_class.return_value = mock_gpio
            
            # Create Relay controller
            controller = RelayController(config)
            
            # Pulse relay
            controller.pulse("relay1", 0.5)
            
            # Check that GPIO controller was called
            mock_gpio.set_output_state.assert_any_call(22, True)  # Activate
            mock_sleep.assert_called_once_with(0.5)
            mock_gpio.set_output_state.assert_any_call(22, False)  # Deactivate
            
            # Check relay state
            assert controller.relays["relay1"]["active"] is False
