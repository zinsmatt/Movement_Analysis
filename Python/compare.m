function [ output_args ] = compare( ca, cb,cref,t )
% subplot(1,2,1);
% plot(t,ca,'r',t,cb,'b',t,cref,'g');
% delta = 10;
% cb = circshift(cb,[0 -delta]);
% cb(1:delta) = 0;
% subplot(1,2,2);
% plot(t,ca,'r',t,cb,'b',t,cref,'g');
% figure;
% subplot(1,2,1);
% plot(t,ca(1,:),'g',t,cref(1,:),'r');
% subplot(1,2,2);
% plot(t,ca(2,:),'g',t,cref(2,:),'r');
deltamax = 20
%ca
diff_ca = [];

for delta = 0:-1:-deltamax,
   idx = 1:size(t,2)+delta;
   ca_dec = circshift(ca,[0 delta]);
   a = ca_dec(:,idx);
   ref = cref(:,idx);
   diff = sum((a-ref).^2,2);
   dtot = sum(diff.^2,1)/size(idx,2);
   diff_ca = [diff_ca dtot];
   fprintf('delta = %d diff = %f\n',delta,dtot);
   
%    figure;
%    subplot(1,2,1);
%    plot(t(idx),a(1,:),'b',t(idx),ref(2,:),'r');
%       plot(t(idx),a(1,:),'b',t(idx),a(2,:),'g',t(idx),ref(1,:),'r',t(idx),ref(2,:),'r');

   hold on;
   
%    subplot(1,2,2);
%    plot(t(idx),a(2,:),'g',t(idx),ref(2,:),'r');
end
diff_cb = [];
for delta = 0:-1:-deltamax,
   cb = circshift(cb,[0 delta]);
   idx = 1:size(t,2)+delta;
   b = cb(:,idx);
   ref = cref(:,idx);
   diff = sum((b-ref).^2,2);
   dtot = sum(diff.^2,1)/size(idx,2);
   diff_cb = [diff_cb dtot];
   fprintf('delta = %d diff = %f\n',delta,dtot);
   
%    figure;
%    subplot(1,2,1);
%    plot(t(idx),b(1,:),'g',t(idx),ref(1,:),'r');
%    subplot(1,2,2);
%    plot(t(idx),b(2,:),'g',t(idx),ref(2,:),'r');
end


fprintf('Main gauche score : %f\n',min(diff_ca));
fprintf('Main droite score : %f\n',min(diff_cb));


end

