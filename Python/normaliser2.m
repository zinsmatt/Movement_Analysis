function [ v_out1, v_out2 ] = normaliser2( v1, v2 )

mini = min([v1;v2]);
% v1 = v1 - mini;
% v2 = v2 - mini;
maxi = max(abs([v1;v2]));
v1 = v1./maxi;
v2 = v2./maxi;

v_out1 = v1;
v_out2 = v2;

end

