--riazzerawifi.lua
-- Starts the portal to choose the wi-fi router to which we have
-- to associate
wifi.sta.disconnect()
wifi.setmode(wifi.STATIONAP)
--ESP SSID generated wiht its chipid
wifi.ap.config({ssid="Mynode-"..node.chipid()
, auth=wifi.OPEN})
enduser_setup.manual(true)
enduser_setup.start(
  function()
    print("Connected to wifi as:" .. wifi.sta.getip())
  end,
  function(err, str)
    print("enduser_setup: Err #" .. err .. ": " .. str)
  end
);
