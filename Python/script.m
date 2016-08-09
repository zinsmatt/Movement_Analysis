clear all;
left = load('data_hand_left.txt');
right = load('data_hand_right.txt');
acc = load('smartphone.dat');

t_init = acc(1,1);
acc(:,1) = (acc(:,1)-t_init)/1000;
subplot(1,3,1);
plot(acc(:,1),acc(:,2),'r',acc(:,1),acc(:,3),'g',acc(:,1),acc(:,4),'b');
hold on;
sx = medfilt1(acc(:,2));
sy = medfilt1(acc(:,3));
sz = medfilt1(acc(:,4));
%s = golayfilt(acc(:,4),3,43);
plot(acc(:,1),sx,'r',acc(:,1),sy,'g',acc(:,1),sz,'b');


ax = sx; ay = sy; az = sz;
subplot(1,3,2);
vx = cumtrapz(acc(:,1),ax);
vy = cumtrapz(acc(:,1),ay);
vz = cumtrapz(acc(:,1),az);
plot(acc(:,1),vx,'r',acc(:,1),vy,'g',acc(:,1),vz,'b');

subplot(1,3,3);
px = cumtrapz(acc(:,1),vx);
py = cumtrapz(acc(:,1),vy);
pz = cumtrapz(acc(:,1),vz);
plot(acc(:,1),px,'r',acc(:,1),py,'g',acc(:,1),pz,'b');

figure();
plot3(px,py,pz);


% x = [0:1:20];
% y = [0:1:20];
% figure();
% plot(x,y,'.'); hold on;
% c = cumtrapz(x,y);
% plot(x,c,'o');hold on;
% v = 0.5*x.^2;
% plot(x,v);



% left(:,3) = 480-left(:,3)
% right(:,3) = 480-right(:,3)
% 
% 
% plot(left(:,2),left(:,3),'r.');
% hold on;
% plot(right(:,2),right(:,3),'b.');
% 
% 
% v = [0 0]
% for i=2:size(left,1),
%     dx  = left(i,2)-left(i-1,2);
%     dy  = left(i,3)-left(i-1,3);
%     dt = (left(i,1)-left(i-1,1))/1000;
%     v = [v; dx/dt dy/dt ];
% end
% plot(left(:,1),v,'.-');
% 
% a = [0]
% for i=2:size(v,1),
%     v_diff = v(i)-v(i-1)
%     d = (left(i,1)-left(i-1,1))/1000;
%     a = [a;v_diff/d];
% end
% 
% plot(left(:,1),a'.');
% 
% 
% freq = []
% for i=2:size(left,1),
%     freq = [freq left(i,1)-left(i-1,1)];
% end
% 
% plot(freq);


% 
% 
% 
% v = [0]
% for i=2:size(left,1),
%     dist = sqrt((left(i,2)-left(i-1,2))^2+(left(i,3)-left(i-1,3))^2);
%     d = (left(i,1)-left(i-1,1))/1000;
%     v = [v;dist/d];
% end
% plot(left(:,1),v,'.-');
% 
% a = [0]
% for i=2:size(v,1),
%     v_diff = v(i)-v(i-1)
%     d = (left(i,1)-left(i-1,1))/1000;
%     a = [a;v_diff/d];
% end
% 
% plot(left(:,1),a'.');
% 
% 
% freq = []
% for i=2:size(left,1),
%     freq = [freq left(i,1)-left(i-1,1)];
% end