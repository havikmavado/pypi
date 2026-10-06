import easygui

# 1. Pergunta inicial
resposta = easygui.ynbox(
    'SOU CHARLIE KIRK, deseja algo?', 'Título', ('Sim', 'Não')
)

if resposta:
  # 2. Reação
  easygui.msgbox('*toma tiro*', 'Ação')

  # 3. Seleção do culpado
  culpado = easygui.buttonbox(
      'QUEM foi o CULPADO?',
      'Culpados',
      ('kirknator', 'jair bolsonaro', 'bola de boliche oniciente'),
  )

  # Se o jogador fechar a janela sem escolher
  if culpado is None:
    easygui.msgbox('O mistério ficou sem solução...', 'Fim')
  else:
    # Caso escolha outro suspeito, revela que Kirknator era o verdadeiro culpado
    if culpado != 'kirknator':
      easygui.msgbox(
          f'Você acusou {culpado}, mas ele era inocente!\n'
          'As evidências apontam para Kirknator!',
          'Reviravolta',
      )

    # 4. Confissão do Kirknator
    easygui.msgbox(
        'Kirknator: "EU CONFESSO! Fui eu, o Kirknator! Eu planejei tudo desde o início!"',
        'Confissão',
    )

    # 5. Julgamento: Soltar ou Deixar Preso
    decisao = easygui.buttonbox(
        'Kirknator confessou o crime! Qual será o destino dele?',
        'Julgamento',
        ('Soltar', 'Deixar Preso'),
    )

    # 6. Desfecho final
    if decisao == 'Soltar':
      easygui.msgbox(
          'Você soltou o Kirknator! Ele saiu rindo e prometeu aprontar de novo.',
          'Resultado',
      )
    elif decisao == 'Deixar Preso':
      easygui.msgbox(
          'Kirknator foi condenado e enviado para a prisão perpétua. Justiça feita!',
          'Resultado',
      )
    else:
      easygui.msgbox('Kirknator aproveitou a indecisão e fugiu!', 'Resultado')

else:
  easygui.msgbox('Você decidiu ignorar e nada aconteceu.', 'Fim')