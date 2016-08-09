clear all;
left = load('data3/data_hand_left.txt');
right = load('data3/data_hand_right.txt');

left(:,3) = 480-left(:,3)
right(:,3) = 480-right(:,3)

t = left(:,1);
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

% v filtered and normalised
subplot(2,4,4);
svxln = normaliser(svxl);
svyln = normaliser(svyl);
plot(t,svxln,'r',t,svyln,'g');



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
subplot(2,4,8);
svxrn = normaliser(svxr);
svyrn = normaliser(svyr);
plot(t,svxrn,'r',t,svyrn,'g');














% 
% a = [0]
% for i=2:size(v,1),
%     v_diff = v(i)-v(i-1)
%     d = (left(i,1)-left(i-1,1))/1000;
%     a = [a;v_diff/d];
% end
% subplot(1,3,3);
% plot(left(:,1),a'.');





% freq = []
% for i=2:size(left,1),
%     freq = [freq left(i,1)-left(i-1,1)];
% end
% 
% plot(freq);





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