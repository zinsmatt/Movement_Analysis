clear all;
close all;
mi12 = load('smartphone.txt');
left = load('data4/data_hand_left.txt');
right = load('data4/data_hand_right.txt');

t = mi12(:,1);
Te = []
for i=2:size(t,1),
    Te = [Te t(i)-t(i-1)]
end
figure()
plot(Te);


a = load('temps_reponse.txt')
plot(a(:,2),'.-b');
xlabel('Réponse');
ylabel('Temps de réponse (en ms)')
axis([1 40 0 50])
grid on


t = left(:,1)
Te = []
for i=2:size(t,1),
    Te = [Te t(i)-t(i-1)]
end
plot(Te,'.-b')
xlabel('Mesure')
ylabel('Période d"echantillonnage (ms)');
axis([1 55 0 100])

mean(Te)
