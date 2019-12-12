lighton=0
tmr.alarm(0,1000,1,function()
if lighton==0 then 
    lighton=1 
    led(512,512,512) 
    -- 512/1024, 50% duty cycle
else 
    lighton=0 
    led(0,0,0) 
end 
end)
