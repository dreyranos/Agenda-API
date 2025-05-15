program AgendaBot;

uses
  System.StartUpCopy,
  FMX.Forms,
  main in 'main.pas' {formPrincipal},
  frm_dia in 'frm_dia.pas' {frameDia: TFrame},
  dm in 'dm.pas' {DataModule1: TDataModule};

{$R *.res}

begin
  Application.Initialize;
  Application.CreateForm(TformPrincipal, formPrincipal);
  Application.CreateForm(TDataModule1, DataModule1);
  Application.Run;
end.
