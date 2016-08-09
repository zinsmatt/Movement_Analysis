function [ v_out ] = normaliser( values )
mini = min(values);
values = values - mini;
maxi = max(values);
values = values./maxi;
v_out = values;
end

