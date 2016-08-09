clear all;
close all;
mi12 = load('data_rapport/smartphone.txt');
left = load('data_rapport/data_hand_left.txt');
right = load('data_rapport/data_hand_right.txt');


tsm = mi12(:,1);
tsm = tsm-tsm(1);
x = mi12(:,2);
y = mi12(:,3);
z = mi12(:,4);
w = ones(size(x,1),1);

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

figure();
acc = coord_2d';
temp = [nouv_coords(1,:); nouv_coords(3,:)];
acc = temp';

t_init = acc(1,1);
tsm = tsm/1000;
acc = [tsm acc];

subplot(2,3,1);
plot(acc(:,1),acc(:,2),'r',acc(:,1),acc(:,3),'g');
sx = medfilt1(acc(:,2));
sy = medfilt1(acc(:,3));
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
% vxn = normaliser(vx);
% vyn = normaliser(vy);
[vxn, vyn] = normaliser2(vx,vy);
plot(acc(:,1),vxn,'r',acc(:,1),vyn,'g');

subplot(2,3,3);
% vxnfn = normaliser(vxnf);
% vynfn = normaliser(vynf);
[vxnfn,vynfn] = normaliser2(vxnf,vynf);
plot(acc(:,1),vxnfn,'r',acc(:,1),vynfn,'g');

%%%%%%%%%%%%%%%%%% position %%%%%%%%%%%%%%%%%
% % position filtree
% figure
% px = cumtrapz(acc(:,1),vx);
% py = cumtrapz(acc(:,1),vy);
% plot(acc(:,1),px,'r',acc(:,1),py,'g');
% % 
% % % position non filtree
% % subplot(2,3,3);
% % pxnf = cumtrapz(acc(:,1),vxnf);
% % pynf = cumtrapz(acc(:,1),vynf);
% % plot(acc(:,1),pxnf,'r',acc(:,1),pynf,'g');
% 
% %trajectoire
% figure();
% min_axis = min([px;py]);
% max_axis = max([px;py]);
% plot(px,py);
% axis square
% axis equal
% axis([min_axis max_axis min_axis max_axis])


% =========== kinect ==========

% rectifier Y car il est dirige vers le bas
left(:,3) = 480-left(:,3)
right(:,3) = 480-right(:,3)
t = left(:,1);
for i=1:size(t,1)-2,
    if t(i)==t(i+1),
        t(i+1) = (t(i)+t(i+2))/2;
    end
end

t = t-t(1);
t = t/1000;

figure();
subplot(2,4,1);
plot(left(:,2),left(:,3),'b.');
subplot(2,4,5);
plot(right(:,2),right(:,3),'b.');



% left hand
vl = [0 0]
for i=2:size(left,1),
    dx  = left(i,2)-left(i-1,2);
    dy  = left(i,3)-left(i-1,3);
    dt = (left(i,1)-left(i-1,1))/1000;
    vl = [vl; dx/dt dy/dt ];
end
subplot(2,4,2);
plot(t,vl(:,1),'r',t,vl(:,2),'g');

% v filtered
svxl = medfilt1(vl(:,1));
svyl = medfilt1(vl(:,2));
subplot(2,4,3);
plot(t,svxl,'r',t,svyl,'g');


% right hand
vr = [0 0]
for i=2:size(left,1),
    dx  = right(i,2)-right(i-1,2);
    dy  = right(i,3)-right(i-1,3);
    dt = (right(i,1)-right(i-1,1))/1000;
    vr = [vr; dx/dt dy/dt ];
end
subplot(2,4,6);
plot(t,vr(:,1),'r',t,vr(:,2),'g');

% v filtered
svxr = medfilt1(vr(:,1));
svyr = medfilt1(vr(:,2));
subplot(2,4,7);
plot(t,svxr,'r',t,svyr,'g');

% v filtered and normalised
% mini = min([svxl;svyl;svxr;svyr]);
% svxln = svxl-mini;
% svyln = svyl-mini;
% svxrn = svxr-mini;
% svyrn = svyr-mini;
% maxi = max([svxln;svyln;svxrn;svxln]);
% svxln = svxln./maxi;
% svyln = svyln./maxi;
% svxrn = svxrn./maxi;
% svyrn = svyrn./maxi;

subplot(2,4,8);
% svxrn = normaliser(svxr);
% svyrn = normaliser(svyr);
[svxrn,svyrn] = normaliser2(svxr,svyr);
% svxrn = medfilt1(svxrn);
% svyrn = medfilt1(svyrn);
plot(t,svxrn,'r',t,svyrn,'g');

subplot(2,4,4);
% svxln = normaliser(svxl);
% svyln = normaliser(svyl);
[svxln,svyln] = normaliser2(svxl,svyl);
% svxln = medfilt1(svxln);
% svyln = medfilt1(svyln);
plot(t,svxln,'r',t,svyln,'g');

%%%%%%%%%%%% essai %%%%%%%%%%%
% sm_tk_x = interp1(acc(:,1),vxnfn,t);
% sm_tk_y = interp1(acc(:,1),vynfn,t);
% figure;
% subplot(1,3,1);
% plot(t,svxln,'r',t,svyln,'g');
% subplot(1,3,2);
% plot(t,svxrn,'r',t,svyrn,'g');
% subplot(1,3,3);
% plot(t,sm_tk_x,'r',t,sm_tk_y,'g');
% 
% figure()
% subplot(1,2,1);
% plot(left(:,2),left(:,3),'O-');hold on;
% quiver(left(:,2),left(:,3),svxln,svyln);
% quiver(left(:,2),left(:,3),sm_tk_x,sm_tk_y,'g');
% 
% 
% subplot(1,2,2);
% plot(right(:,2),right(:,3),'O-');hold on;
% quiver(right(:,2),right(:,3),svxrn,svyrn);
% quiver(right(:,2),right(:,3),sm_tk_x,sm_tk_y,'g');
% 
% 
% 
% plot(left(:,2),left(:,3),'b.');
% subplot(2,4,5);
% plot(right(:,2),right(:,3),'b.');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



% interpolation
tt = linspace(0,min(max(tsm),max(t)));
sm_interx = interp1(acc(:,1),vxnfn,tt);
sm_intery = interp1(acc(:,1),vynfn,tt);
l_interx = interp1(t,svxln,tt);
l_intery = interp1(t,svyln,tt);
r_interx = interp1(t,svxrn,tt);
r_intery = interp1(t,svyrn,tt);

figure();

subplot(1,3,1);
plot(tt,sm_interx,'r.',tt,sm_intery,'g.');
subplot(1,3,2);
plot(tt,l_interx,'r.',tt,l_intery,'g.');
subplot(1,3,3);
plot(tt,r_interx,'r.',tt,r_intery,'g.');

% figure
% subplot(1,2,1);
% plot(tt,sm_interx,tt,l_interx,tt,r_interx);
% subplot(1,2,2);
% plot(tt,sm_interx-l_interx,tt,sm_interx-r_interx);
% sum((sm_interx-l_interx).^2)
% sum((sm_interx-r_interx).^2)
% figure
% subplot(1,2,1);
% plot(tt,sm_intery,tt,l_intery,tt,r_intery);
% subplot(1,2,2);
% plot(tt,sm_intery-l_intery,tt,sm_intery-r_intery);
% sum((sm_intery-l_intery).^2)
% sum((sm_intery-r_intery).^2)



% =========== essai de comparaison ===============
% ---------- essai 3 ---------------------
compare([l_interx;l_intery],[r_interx;r_intery],[sm_interx;sm_intery],tt);


% ---------- essai 1 ---------------------

% diff_lx = sm_interx-l_interx;
% diff_ly = sm_intery-l_intery;
% diff_l = sqrt(diff_lx.^2+diff_ly.^2);
% 
% diff_rx = sm_interx-r_interx;
% diff_ry = sm_intery-r_intery;
% diff_r = sqrt(diff_rx.^2+diff_ry.^2);
% 
% v_diff_l = sum(diff_l,2)/size(tt,2);
% v_diff_r = sum(diff_r,2)/size(tt,2);
% 
% fprintf('Difference main gauche = %f\n',v_diff_l);
% fprintf('Difference main droite = %f\n',v_diff_r);

% ---------- essai 2 ---------------------
% DL_x = sum((diff_lx).^2,2);
% DL_y = sum((diff_ly).^2,2);
% DR_x = sum((diff_rx).^2,2);
% DR_y = sum((diff_ry).^2,2);
% 
% fprintf('main gauche : diff x = %f\n',sum((diff_lx).^2,2)/size(tt,2));
% fprintf('main gauche : diff y = %f\n',sum((diff_ly).^2,2)/size(tt,2));
% fprintf('main droite : diff x = %f\n',sum((diff_rx).^2,2)/size(tt,2));
% fprintf('main droite : diff y = %f\n',sum((diff_ry).^2,2)/size(tt,2));
% 
% fprintf('Main gauche score : %f\n',(DL_x^2+DL_y^2)/size(tt,2));
% fprintf('Main droite score : %f\n',(DR_x^2+DL_y^2)/size(tt,2));



x = [0]
y = [0]
for i=1:size(sm_interx,2)-1
    xn = x(i)+sm_interx(i+1);
    yn = y(i)+sm_intery(i+1);
    x = [x xn];
    y = [y yn];
end

xl = [0]
yl = [0]
for i=1:size(sm_interx,2)-1
    xn = xl(i)+l_interx(i+1);
    yn = yl(i)+l_intery(i+1);
    xl = [xl xn];
    yl = [yl yn];
end

xr = [0]
yr = [0]
for i=1:size(sm_interx,2)-1
    xn = xr(i)+r_interx(i+1);
    yn = yr(i)+r_intery(i+1);
    xr = [xr xn];
    yr = [yr yn];
end

figure();
subplot(1,3,2);
plot(x(1:60),y(1:60));
subplot(1,3,1);
plot(xl,yl);
subplot(1,3,3);
plot(xr,yr);