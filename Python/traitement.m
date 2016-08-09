clear all;
mi12 = load('data3/smartphone.txt');

%mi12 = load('data.txt');

t = mi12(:,1);
t = t-t(1);
x = mi12(:,2);
y = mi12(:,3);
z = mi12(:,4);
w = ones(size(x,1),1);
subplot(1,3,1);
plot(t,x,'r',t,y,'g',t,z,'b');

coords = [x y z w];

rot = cell(size(mi12,1));
for i=1:size(mi12,1),
  mat = reshape(mi12(i,5:end),3,3)';
  mat = [mat;0 0 0];
  mat = [mat [0;0;0;1]];
  rot{i} = mat;
end

nouv_coords = [];
for i=1:size(x,1),
  temp = rot{i}*coords(i,:)';
  nouv_coords = [nouv_coords temp];
end

coord_2d = [];
for i=1:size(nouv_coords,2),
  temp = [coords(i,1);nouv_coords(3,i)];
  coord_2d = [coord_2d temp];
end

subplot(1,3,2);
plot(t,nouv_coords(1,:),'r',t,nouv_coords(2,:),'g',t,nouv_coords(3,:),'b');

subplot(1,3,3);
plot(t,coord_2d(1,:),'r',t,coord_2d(2,:),'b');

figure();
% -------- MATLAB ------------
%pkg load signal

acc = coord_2d';
temp = [nouv_coords(1,:); nouv_coords(3,:)];
acc = temp';

t_init = acc(1,1);
t = t/1000;
acc = [t acc];

subplot(2,3,1);
plot(acc(:,1),acc(:,2),'r',acc(:,1),acc(:,3),'g');
sx = medfilt1(acc(:,2));
sy = medfilt1(acc(:,3));
%s = golayfilt(acc(:,4),3,43);
subplot(2,3,4);
plot(acc(:,1),sx,'r',acc(:,1),sy,'g');

% vitesse filtree
ax = sx; ay = sy;
vx = cumtrapz(acc(:,1),ax);
vy = cumtrapz(acc(:,1),ay);
subplot(2,3,5);
plot(acc(:,1),vx,'r',acc(:,1),vy,'g');

% vitesse non filtree
vxnf = cumtrapz(acc(:,1),acc(:,2));
vynf = cumtrapz(acc(:,1),acc(:,3));
subplot(2,3,2);
plot(acc(:,1),vxnf,'r',acc(:,1),vynf,'g');


% vitesses normalisees
subplot(2,3,6);
vxn = normaliser(vx);
vyn = normaliser(vy);
plot(acc(:,1),vxn,'r',acc(:,1),vyn,'g');

subplot(2,3,3);
vxnfn = normaliser(vxnf);
vynfn = normaliser(vynf);
plot(acc(:,1),vxnfn,'r',acc(:,1),vynfn,'g');


% position filtree
% subplot(2,3,6);
% px = cumtrapz(acc(:,1),vx);
% py = cumtrapz(acc(:,1),vy);
% plot(acc(:,1),px,'r',acc(:,1),py,'g');
% 
% % position non filtree
% subplot(2,3,3);
% pxnf = cumtrapz(acc(:,1),vxnf);
% pynf = cumtrapz(acc(:,1),vynf);
% plot(acc(:,1),pxnf,'r',acc(:,1),pynf,'g');






% %trajectoire
% figure();
% min_axis = min([px;py]);
% max_axis = max([px;py]);
% plot(px,py);
% axis square
% axis equal
% axis([min_axis max_axis min_axis max_axis])
